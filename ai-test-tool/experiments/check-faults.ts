import assert from 'node:assert/strict';
import path from 'node:path';
import { createServer } from 'node:net';
import { setTimeout as delay } from 'node:timers/promises';
import { randomUUID } from 'node:crypto';
import { mkdir } from 'node:fs/promises';
import { TestRunner } from '../src/runner.ts';
import { RunStore } from '../src/store.ts';
import { parseJUnit } from '../src/junit.ts';
import { analyzeRun } from '../src/gemini.ts';
import type { Run } from '../src/types.ts';
import { evidenceRoot, saveEvidence } from './evidence.ts';

const results: any[] = [];
try { parseJUnit('<testsuite><testcase></testsuite>'); results.push({ id: 'FAULT-XML', passed: false }); }
catch (error: any) { results.push({ id: 'FAULT-XML', expected: 'Từ chối XML hỏng', actual: error.message, passed: /XML không hợp lệ/.test(error.message), type: 'input-validation' }); }

for (const kind of ['cancelled', 'timeout'] as const) {
  const store = new RunStore(path.join(evidenceRoot, 'fault-artifacts', kind));
  const runner = new TestRunner(store, async (_, cwd) => ({ executable: process.execPath, args: ['-e', 'console.log("Controlled Node process: test tool cancellation/timeout; not an HSK test"); setInterval(()=>{},1000)'], cwd }));
  const run = await runner.start('vitest-core', 10);
  try {
    if (kind === 'cancelled') {
      for (let i = 0; i < 200 && !runner.active?.child?.pid; i++) await delay(20);
      assert.ok(runner.active?.child?.pid);
      await runner.cancel(run.id);
    }
    await runner.active?.done;
    const saved = await store.get(run.id);
    results.push({ id: kind === 'cancelled' ? 'FAULT-CANCEL' : 'FAULT-TIMEOUT', expected: kind, actual: saved?.status,
      passed: saved?.status === kind, duration: saved?.duration, artifactDirectory: `fault-artifacts/${kind}/${run.id}`,
      type: 'controlled-node-process', notWebsiteTest: true });
  } finally { await runner.shutdown(); }
}

const socket = createServer();
await new Promise<void>(resolve => socket.listen(0, '127.0.0.1', resolve));
const address = socket.address();
assert.ok(address && typeof address === 'object');
const closedPort = address.port;
await new Promise<void>((resolve, reject) => socket.close(error => error ? reject(error) : resolve()));
const run: Run = { id: randomUUID(), name: 'Controlled connection failure', groupId: 'experiment', engine: 'import', source: 'import', status: 'error', startedAt: new Date().toISOString(), duration: 0, timeoutSeconds: 0, error: 'Controlled fault' };
const originalKey = process.env.GEMINI_API_KEY;
try {
  process.env.GEMINI_API_KEY = 'fault-injection-placeholder-not-a-real-key';
  await analyzeRun(run, '', async () => fetch(`http://127.0.0.1:${closedPort}`, { signal: AbortSignal.timeout(3000) }));
  results.push({ id: 'FAULT-GEMINI-CONNECTION', passed: false });
} catch (error: any) {
  results.push({ id: 'FAULT-GEMINI-CONNECTION', expected: 'Lỗi kết nối được trả về, trạng thái test không đổi', actual: error.message,
    actualCause: error.cause?.code, retainedRunStatus: run.status, passed: error.cause?.code === 'ECONNREFUSED' && run.status === 'error',
    type: 'controlled-local-connection-refusal', realGeminiRequest: false });
} finally { if (originalKey === undefined) delete process.env.GEMINI_API_KEY; else process.env.GEMINI_API_KEY = originalKey; }
await mkdir(evidenceRoot, { recursive: true });
await saveEvidence('fault-scenarios.json', { checkedAt: new Date().toISOString(), results });
console.log(JSON.stringify({ step: 3, passed: results.filter(result => result.passed).length, total: results.length }));
if (results.some(result => !result.passed)) process.exitCode = 1;
