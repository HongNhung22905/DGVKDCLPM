import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { createConnection } from 'node:net';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { analyzeRun } from '../src/gemini.ts';
import { parseJUnit } from '../src/junit.ts';
import { validateTestEnvironment } from '../src/hsk-test-environment.ts';
import { repoRoot, toolRoot } from '../src/config.ts';
import { redact } from '../src/redact.ts';
import type { Run } from '../src/types.ts';
import { evidenceRoot, loadEvidence, saveEvidence } from './evidence.ts';

const exec = promisify(execFile);
const childEnv = { ...process.env };
delete childEnv.GEMINI_API_KEY;
const fixtures: any[] = [];
function add(id: string, category: string, knownCause: string, expectedChecks: string[], log: string, source: string, status: Run['status'] = 'error') {
  fixtures.push({ id, category, knownCause, expectedChecks, log: redact(log), source, status });
}
const historical = parseJUnit(await readFile(path.join(repoRoot, 'selenium-tests/FC-05-results.xml'), 'utf8'));
add('AI-01', 'assertion', 'Chuỗi nhận được là 100%, chuỗi mong đợi là 100; khác ký tự %. Chưa có đặc tả để quyết định sửa sản phẩm hay assertion.', ['Đối chiếu yêu cầu định dạng điểm và giá trị DOM', 'Xác minh dữ liệu/kỳ vọng trước khi sửa'], historical.cases[0].message + '\n' + historical.cases[0].details, 'historical-hsk-xml', 'failed');
try { await exec(path.join(toolRoot, '.venv', 'Scripts', 'python.exe'), ['-c', 'import hsk_missing_test_dependency_20261019'], { env: childEnv, windowsHide: true }); }
catch (error: any) { add('AI-02', 'environment', 'Thiếu module hsk_missing_test_dependency_20261019 trong Python đang dùng; tên module được cố ý tạo để gây lỗi.', ['Kiểm tra interpreter và môi trường dependency', 'Không thay assertion để xử lý lỗi import'], error.stderr || error.message, 'controlled-python-import'); }
try { await exec(path.join(evidenceRoot, 'nonexistent-python.exe'), ['--version'], { env: childEnv, windowsHide: true }); }
catch (error: any) { add('AI-03', 'environment', 'Đường dẫn executable Python không tồn tại; hệ điều hành trả ENOENT trước khi chạy test.', ['Kiểm tra PYTHON_EXECUTABLE hoặc PATH', 'Xác nhận file thực thi tồn tại'], `${error.code}: ${error.message}`, 'controlled-missing-executable'); }
try { await exec(process.execPath, ['-e', 'require("node:assert/strict").equal(79,80)'], { env: childEnv, windowsHide: true }); }
catch (error: any) { add('AI-04', 'assertion', 'Tiến trình Node so sánh actual=79 với expected=80 nên assertion thất bại. Không có nghiệp vụ để suy ra giá trị nào đúng.', ['Kiểm tra input/fixture và phép tính tạo giá trị', 'Đối chiếu đặc tả trước khi thay expected'], error.stderr || error.message, 'controlled-node-assertion', 'failed'); }
const faults = await loadEvidence('fault-scenarios.json');
const timeout = faults.results.find((item: any) => item.id === 'FAULT-TIMEOUT');
add('AI-05', 'timeout', 'Tiến trình Node cố ý chạy vô hạn; runner dừng sau giới hạn 10 giây, không có XML hoàn chỉnh.', ['Xem nhật ký và tiến trình bị treo', 'Không tự tăng timeout để coi là đạt'], `Run status: timeout. Time limit: 10 seconds. Elapsed: ${timeout.duration}. Controlled Node process log: setInterval keeps running, runner terminated process tree, no complete JUnit XML.`, 'controlled-runner-timeout', 'timeout');

const server = createServer((request, response) => {
  if (request.url === '/slow') { const timer = setTimeout(() => { response.end('late'); }, 500); response.on('close', () => clearTimeout(timer)); return; }
  response.writeHead(request.url === '/unauthorized' ? 401 : 403, { 'Content-Type': 'application/json' });
  response.end(JSON.stringify({ error: request.url === '/unauthorized' ? 'Missing bearer token' : 'Authenticated role learner does not have admin permission' }));
});
await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve));
const address = server.address();
if (!address || typeof address === 'string') throw new Error('Không lấy được địa chỉ HTTP fixture.');
const base = `http://127.0.0.1:${address.port}`;
try {
  try { await fetch(base + '/slow', { signal: AbortSignal.timeout(30) }); }
  catch (error: any) { add('AI-06', 'timeout', 'HTTP fixture chờ 500 ms, client chỉ đợi 30 ms nên AbortSignal phát TimeoutError.', ['Đối chiếu deadline client với latency server', 'Kiểm tra dịch vụ chậm và request thực tế'], `GET /slow. Client timeout=30ms. ${error.name}: ${error.message}`, 'controlled-http-timeout', 'timeout'); }
  for (const [id, route, cause, checks] of [
    ['AI-07', '/unauthorized', 'HTTP fixture trả 401 vì request không có bearer token.', ['Kiểm tra token/cookie được gửi trong request', 'Thực hiện hoặc kiểm tra luồng đăng nhập']],
    ['AI-08', '/forbidden', 'HTTP fixture trả 403 vì role learner thiếu quyền admin, dù đã xác thực.', ['Kiểm tra role/quyền của tài khoản', 'Không coi đăng nhập lại là đủ để có quyền admin']],
  ] as const) {
    const response = await fetch(base + route);
    add(id, 'authentication', cause, [...checks], `GET ${route} -> HTTP ${response.status}\n${await response.text()}`, 'controlled-http-auth');
  }
} finally { server.closeAllConnections(); await new Promise<void>(resolve => server.close(() => resolve())); }
try {
  await new Promise<void>((resolve, reject) => { const socket = createConnection({ host: '127.0.0.1', port: address.port }); socket.once('error', reject); socket.once('connect', () => { socket.destroy(); resolve(); }); });
} catch (error: any) { add('AI-09', 'database', 'Cổng TCP được đóng trước khi client kết nối: ECONNREFUSED. Chưa đến bước xác thực PostgreSQL.', ['Kiểm tra host/port và PostgreSQL có lắng nghe', 'Không kết luận sai mật khẩu từ ECONNREFUSED'], `PostgreSQL connection attempt to isolated local test endpoint. ${error.code}: ${error.message}`, 'controlled-local-db-port'); }
try { validateTestEnvironment({ HSK_TEST_BRANCH: 'hsk-test-missing' }); }
catch (error: any) { add('AI-10', 'database', 'DATABASE_URL của môi trường kiểm thử chưa được cấu hình nên launcher từ chối trước khi mở kết nối DB.', ['Điền URL của branch kiểm thử trong .env.hsk-test', 'Không dùng database hiện tại để thay thế'], error.message, 'controlled-test-db-config'); }
if (fixtures.length !== 10) throw new Error(`Chưa tạo đủ 10 lỗi: ${fixtures.length}`);
await saveEvidence('ai-dataset.json', { createdAt: new Date().toISOString(), note: '1 lỗi HSK lịch sử và 9 lỗi có kiểm soát của môi trường/fixture; không gọi đây là 10 lỗi thực tế của website. Known cause được lưu trước khi gọi AI và không được gửi cho model.', fixtures });
const evaluations: any[] = [];
let cursor = 0;
async function worker() {
  while (cursor < fixtures.length) {
    const fixture = fixtures[cursor++];
    const run: Run = { id: randomUUID(), name: `${fixture.id}: kiểm thử lỗi`, groupId: 'ai-evaluation', engine: 'import', source: 'import', status: fixture.status, startedAt: new Date().toISOString(), duration: 0, timeoutSeconds: 0, error: fixture.log };
    const started = performance.now();
    let result: Record<string, unknown>;
    try { result = { status: 'answered', analysis: await analyzeRun(run, fixture.log) }; }
    catch (error: any) { result = { status: 'unavailable', error: error.message }; }
    evaluations.push({ id: fixture.id, ...result, elapsedSeconds: (performance.now() - started) / 1000 });
    await saveEvidence('ai-responses.json', { checkedAt: new Date().toISOString(), model: process.env.GEMINI_MODEL, results: evaluations.toSorted((a, b) => a.id.localeCompare(b.id)) });
    console.log(JSON.stringify({ id: fixture.id, status: result.status }));
  }
}
await Promise.all([worker(), worker()]);
