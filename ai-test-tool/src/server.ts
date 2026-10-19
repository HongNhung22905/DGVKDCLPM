import { createServer } from 'node:http';
import type { IncomingMessage, ServerResponse } from 'node:http';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { groups, publicRoot, MAX_XML_BYTES, MAX_LOG_BYTES } from './config.ts';
import { RunStore } from './store.ts';
import { TestRunner } from './runner.ts';
import { parseJUnit, reportStatus } from './junit.ts';
import { analyzeRun } from './gemini.ts';
import { redact } from './redact.ts';
import type { Run } from './types.ts';

function json(response: ServerResponse, code: number, body: unknown) {
  response.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  response.end(JSON.stringify(body));
}
async function body(request: IncomingMessage): Promise<Record<string, unknown>> {
  if (!request.headers['content-type']?.startsWith('application/json')) throw new Error('Yêu cầu cần Content-Type application/json.');
  const chunks: Buffer[] = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_XML_BYTES * 2) throw new Error('Dữ liệu yêu cầu vượt giới hạn.');
    chunks.push(chunk);
  }
  try {
    const value = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error();
    return value;
  } catch { throw new Error('Nội dung JSON không hợp lệ.'); }
}
const notFound = () => Object.assign(new Error('Không tìm thấy dữ liệu.'), { statusCode: 404 });

export async function createApp(store = new RunStore()) {
  await store.recover();
  const runner = new TestRunner(store);
  const analyzing = new Set<string>();
  const server = createServer(async (request, response) => {
    response.setHeader('X-Content-Type-Options', 'nosniff');
    response.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");
    try {
      const host = request.headers.host;
      if (!host || !/^(localhost|127\.0\.0\.1)(:\d+)?$/.test(host)) throw Object.assign(new Error('Chỉ hỗ trợ truy cập local.'), { statusCode: 403 });
      if (request.headers.origin && request.headers.origin !== `http://${host}`) throw Object.assign(new Error('Origin không hợp lệ.'), { statusCode: 403 });
      const url = new URL(request.url || '/', `http://${host}`);
      const method = request.method;
      if (method === 'GET' && url.pathname === '/api/config') return json(response, 200, {
        groups, gemini: { configured: !!process.env.GEMINI_API_KEY?.trim(), model: process.env.GEMINI_MODEL || 'gemini-flash-latest' },
        activeRunId: runner.active?.run.id ?? null,
      });
      if (method === 'GET' && url.pathname === '/api/runs') {
        const runs = await store.list();
        return json(response, 200, runs.map(({ report, analysis, ...run }) => ({ ...run, summary: report?.summary, analysisAvailable: !!analysis })));
      }
      if (method === 'POST' && url.pathname === '/api/runs') {
        const input = await body(request);
        if (typeof input.groupId !== 'string' || (input.timeoutSeconds !== undefined && typeof input.timeoutSeconds !== 'number')) throw new Error('Nhóm test hoặc giới hạn thời gian không hợp lệ.');
        if (runner.active) return json(response, 409, { error: 'Đang có một nhóm test chạy. Hãy đợi hoặc dừng lần chạy hiện tại.' });
        return json(response, 202, await runner.start(input.groupId, input.timeoutSeconds as number | undefined));
      }
      if (method === 'POST' && url.pathname === '/api/import') {
        const input = await body(request);
        if (typeof input.xml !== 'string' || typeof input.filename !== 'string' || !input.filename.toLowerCase().endsWith('.xml')) throw new Error('Hãy chọn tệp .xml.');
        const report = parseJUnit(input.xml);
        const run: Run = { id: randomUUID(), groupId: 'import', name: path.basename(input.filename.replaceAll('\\', '/')).slice(0, 160), engine: 'import', source: 'import',
          status: reportStatus(report), startedAt: new Date().toISOString(), finishedAt: new Date().toISOString(), duration: report.duration,
          timeoutSeconds: 0, report, reportFile: 'report.xml' };
        await store.save(run);
        await writeFile(path.join(store.directory(run.id), 'report.xml'), input.xml, 'utf8');
        return json(response, 201, run);
      }
      const match = url.pathname.match(/^\/api\/runs\/([a-f0-9-]{36})(?:\/(cancel|analysis|log|xml))?$/i);
      if (match) {
        const [, id, action] = match;
        const run = runner.active?.run.id === id ? structuredClone(runner.active.run) : await store.get(id);
        if (!run) throw notFound();
        if (!action && method === 'GET') return json(response, 200, { ...run, analyzing: analyzing.has(id) });
        if (action === 'cancel' && method === 'POST') {
          await body(request);
          await runner.cancel(id);
          return json(response, 202, { message: 'Đang dừng lần chạy.' });
        }
        if (action === 'log' && method === 'GET') {
          let log = '';
          if (runner.active?.run.id === id) log = runner.active.log;
          else { try { log = await readFile(path.join(store.directory(id), 'output.log'), 'utf8'); } catch { /* Báo cáo nhập không có log. */ } }
          return json(response, 200, { log: redact(log.slice(-MAX_LOG_BYTES)) });
        }
        if (action === 'xml' && method === 'GET') {
          if (!run.reportFile) throw notFound();
          const xml = await readFile(path.join(store.directory(id), 'report.xml'));
          response.writeHead(200, { 'Content-Type': 'application/xml; charset=utf-8', 'Content-Disposition': 'attachment; filename="report.xml"' });
          return response.end(xml);
        }
        if (action === 'analysis' && method === 'POST') {
          await body(request);
          if (analyzing.has(id)) return json(response, 409, { error: 'Đang phân tích lần chạy này.' });
          if (run.analysis) return json(response, 200, run.analysis);
          analyzing.add(id);
          try {
            let log = '';
            try { log = await readFile(path.join(store.directory(id), 'output.log'), 'utf8'); } catch { /* XML nhập có thể không có log. */ }
            run.analysis = await analyzeRun(run, log);
            await store.save(run);
            return json(response, 200, run.analysis);
          } finally { analyzing.delete(id); }
        }
      }
      const assets: Record<string, [string, string]> = {
        '/': ['index.html', 'text/html; charset=utf-8'], '/app.js': ['app.js', 'text/javascript; charset=utf-8'], '/styles.css': ['styles.css', 'text/css; charset=utf-8'],
      };
      if (method === 'GET' && assets[url.pathname]) {
        const [file, contentType] = assets[url.pathname];
        const content = await readFile(path.join(publicRoot, file));
        response.writeHead(200, { 'Content-Type': contentType, 'Cache-Control': 'no-cache' });
        return response.end(content);
      }
      throw notFound();
    } catch (error: any) {
      if (!response.headersSent) json(response, error.statusCode || 400, { error: redact(error.name === 'TimeoutError' ? 'Gemini chưa phản hồi sau 60 giây. Hãy thử lại.' : error.message || 'Không thể xử lý yêu cầu.') });
      else response.end();
    }
  });
  return { server, runner, store };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 4317);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('PORT phải từ 1 đến 65535.');
  const { server, runner } = await createApp();
  server.on('error', error => { console.error(`Không mở được công cụ: ${error.message}`); process.exitCode = 1; });
  server.listen(port, '127.0.0.1', () => console.log(`HSK Test Lab: http://localhost:${port}`));
  let closing = false;
  const stop = async () => {
    if (closing) return;
    closing = true;
    await runner.shutdown();
    server.close();
    server.closeAllConnections();
  };
  process.on('SIGINT', stop);
  process.on('SIGTERM', stop);
}
