import { cp, mkdir, readFile, readdir, symlink, writeFile, unlink } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { frontendRoot, toolRoot } from './config.ts';
import { loadTestEnvironment } from './hsk-test-environment.ts';

// Kiểm tra toàn bộ cấu hình TRƯỚC khi khởi động Next hoặc mở kết nối database.
const config = await loadTestEnvironment().catch((error: Error) => { console.error(error.message); process.exit(1); });
try {
  await fetch('http://127.0.0.1:3000', { signal: AbortSignal.timeout(1500) });
  throw new Error('Cổng 3000 đang được sử dụng. Dừng server local đó trước; công cụ không tự đóng tiến trình khác.');
} catch (error: any) { if (!error.cause) throw error; }
const id = randomUUID();
const snapshot = path.join(toolRoot, 'data', 'hsk-test-app', id);
await mkdir(snapshot, { recursive: true });
const excluded = new Set(['node_modules', '.next', 'coverage-whitebox', '.git']);
for (const entry of await readdir(frontendRoot, { withFileTypes: true })) {
  if (excluded.has(entry.name) || entry.name.startsWith('.env') || entry.name.endsWith('.tsbuildinfo')) continue;
  await cp(path.join(frontendRoot, entry.name), path.join(snapshot, entry.name), { recursive: true });
}
await symlink(path.join(frontendRoot, 'node_modules'), path.join(snapshot, 'node_modules'), process.platform === 'win32' ? 'junction' : 'dir');
// Không ghi connection string vào snapshot. Chỉ truyền cho tiến trình kiểm thử này.
process.env.DATABASE_URL = config.databaseUrl;
process.env.NEXTAUTH_SECRET = config.authSecret;
process.env.NODE_ENV = 'development';
process.env.NEXT_TELEMETRY_DISABLED = '1';
// HSK đọc public/data và Tailwind config theo cwd; dùng đúng thư mục snapshot.
process.chdir(snapshot);
const require = createRequire(path.join(frontendRoot, 'package.json'));
const next = require('next');
const app = next({ dev: true, dir: snapshot, hostname: 'localhost', port: 3000 });
await app.prepare();
const handler = app.getRequestHandler();
const markerFile = path.join(toolRoot, 'data', 'hsk-test-server.json');
const marker = { environmentId: id, branch: config.branch, pid: process.pid, origin: 'http://localhost:3000', sourceDirectory: frontendRoot, snapshotDirectory: snapshot, startedAt: new Date().toISOString() };
const server = createServer((request, response) => {
  if (request.url === '/__hsk-test-environment') {
    response.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
    response.end(JSON.stringify({ environmentId: id, branch: config.branch }));
    return;
  }
  void handler(request, response);
});
server.on('error', error => { console.error(`Không mở được HSK kiểm thử: ${error.message}`); process.exitCode = 1; });
await new Promise<void>((resolve, reject) => { server.once('error', reject); server.listen(3000, '127.0.0.1', resolve); });
await writeFile(markerFile, JSON.stringify(marker, null, 2));
console.log(`HSK KIỂM THỬ: http://localhost:3000 | branch ${config.branch} | snapshot ${id}`);
let stopping = false;
const stop = async () => {
  if (stopping) return;
  stopping = true;
  try { const saved = JSON.parse(await readFile(markerFile, 'utf8')); if (saved.environmentId === id) await unlink(markerFile); } catch { /* Không xoá marker của tiến trình khác. */ }
  server.closeAllConnections();
  server.close();
  await app.close();
  process.exit(0);
};
process.on('SIGINT', stop);
process.on('SIGTERM', stop);
