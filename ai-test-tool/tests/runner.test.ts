import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { randomUUID } from 'node:crypto';
import { TestRunner } from '../src/runner.ts';
import { RunStore } from '../src/store.ts';
import type { Run } from '../src/types.ts';

async function setup(t: any, script: string) {
  const directory = await mkdtemp(path.join(tmpdir(), 'hsk-runner-'));
  const store = new RunStore(directory);
  const runner = new TestRunner(store, async (_, cwd) => ({ executable: process.execPath, args: ['-e', script], cwd }));
  t.after(async () => { await runner.shutdown(); await rm(directory, { recursive: true, force: true }); });
  return { runner, store };
}
async function waitForChild(runner: TestRunner) {
  for (let attempt = 0; attempt < 100 && !runner.active?.child; attempt++) await delay(25);
  assert.ok(runner.active?.child?.pid, 'phải có tiến trình test đang chạy');
}
test('chạy tiến trình thật, đọc XML và giữ lịch sử sau khi mở store mới', async t => {
  const { runner, store } = await setup(t, `require('fs').writeFileSync('report.xml','<testsuite tests="2"><testcase name="ok"/><testcase name="bad"><failure message="expected 80"/></testcase></testsuite>'); console.log('finished'); process.exitCode=1;`);
  const run = await runner.start('vitest-all');
  await runner.active?.done;
  const saved = await new RunStore(store.root).get(run.id);
  assert.equal(saved?.status, 'failed');
  assert.equal(saved?.report?.summary.failed, 1);
  assert.equal(saved?.exitCode, 1);
  assert.match(await readFile(path.join(store.directory(run.id), 'output.log'), 'utf8'), /finished/);
});
test('thoát 0 nhưng không có XML vẫn là lỗi thực thi', async t => {
  const { runner, store } = await setup(t, 'console.log("no report")');
  const run = await runner.start('vitest-core');
  await runner.active?.done;
  assert.equal((await store.get(run.id))?.status, 'error');
});
test('giới hạn một lần chạy và dừng được tiến trình đang chạy', async t => {
  const { runner, store } = await setup(t, 'setInterval(()=>console.log("working"), 100)');
  const run = await runner.start('vitest-core');
  await assert.rejects(runner.start('vitest-gate'), /Đang có/);
  await waitForChild(runner);
  const done = runner.active?.done;
  await runner.cancel(run.id);
  await done;
  assert.equal((await store.get(run.id))?.status, 'cancelled');
  assert.equal(runner.active, undefined);
});
test('hết thời gian dừng tiến trình và không ghi PASS', { timeout: 20000 }, async t => {
  const { runner, store } = await setup(t, 'setInterval(()=>{},1000)');
  const run = await runner.start('vitest-core', 10);
  await runner.active?.done;
  assert.equal((await store.get(run.id))?.status, 'timeout');
});
test('khôi phục lần chạy bị gián đoạn khi khởi động lại', async t => {
  const { store } = await setup(t, '');
  const run: Run = { id: randomUUID(), groupId: 'vitest-core', name: 'unfinished', engine: 'vitest', source: 'execution', status: 'running', startedAt: new Date().toISOString(), duration: 0, timeoutSeconds: 120 };
  await store.save(run);
  await new RunStore(store.root).recover();
  assert.equal((await store.get(run.id))?.status, 'interrupted');
  assert.throws(() => store.directory('../../outside'), /không hợp lệ/);
});
test('không thực thi nhóm tùy ý hoặc thời gian không hợp lệ', async t => {
  const { runner } = await setup(t, 'throw new Error("must not execute")');
  await assert.rejects(runner.start('cmd /c echo unexpected'), /không hợp lệ/);
  await assert.rejects(runner.start('vitest-all', -1), /10 đến 7200/);
});
