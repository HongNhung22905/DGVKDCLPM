import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { randomUUID, createHash } from 'node:crypto';
import { repoRoot } from '../src/config.ts';
import { parseJUnit, reportStatus } from '../src/junit.ts';
import { RunStore } from '../src/store.ts';
import { analyzeRun, analysisContext } from '../src/gemini.ts';
import type { Run } from '../src/types.ts';
import { saveEvidence } from './evidence.ts';

const source = 'selenium-tests/FC-05-results.xml';
const xml = await readFile(path.join(repoRoot, source), 'utf8');
const report = parseJUnit(xml);
const store = new RunStore();
const run: Run = {
  id: randomUUID(), groupId: 'import', name: 'Thực nghiệm Gemini — FC-05 (báo cáo lịch sử)',
  engine: 'import', source: 'import', status: reportStatus(report), report,
  startedAt: new Date().toISOString(), finishedAt: new Date().toISOString(), duration: report.duration,
  timeoutSeconds: 0, reportFile: 'report.xml',
};
await store.save(run);
await writeFile(path.join(store.directory(run.id), 'report.xml'), xml, 'utf8');
const started = performance.now();
let service: Record<string, unknown> = {};
let outcome: Record<string, unknown>;
try {
  run.analysis = await analyzeRun(run, '', async (url, options) => {
    const response = await fetch(url, options);
    const copy = await response.clone().json() as any;
    service = { httpStatus: response.status, status: copy.error?.status ?? 'OK', message: copy.error?.message ?? '', finishReason: copy.candidates?.[0]?.finishReason ?? null };
    return response;
  });
  await store.save(run);
  outcome = { status: 'success', analysis: run.analysis };
} catch (error: any) {
  outcome = { status: 'service-unavailable', error: error.message };
}
await saveEvidence('gemini-connection.json', {
  checkedAt: new Date().toISOString(), model: process.env.GEMINI_MODEL || 'gemini-flash-latest',
  source, sourceSha256: createHash('sha256').update(xml).digest('hex'), runId: run.id,
  knownObservation: 'Giá trị hiển thị 100% khác chuỗi kỳ vọng 100. Đây là nguyên nhân trực tiếp của assertion; chưa kết luận lỗi nghiệp vụ.',
  sourceIsHistorical: true, contextSent: JSON.parse(analysisContext(run, '')),
  ...outcome, service, elapsedSeconds: (performance.now() - started) / 1000,
});
console.log(JSON.stringify({ step: 1, outcome: outcome.status, ...service, runId: run.id }));
