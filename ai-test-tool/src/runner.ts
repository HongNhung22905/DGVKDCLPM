import { spawn } from 'node:child_process';
import type { ChildProcess } from 'node:child_process';
import { existsSync } from 'node:fs';
import { access, readFile, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { toolRoot, frontendRoot, seleniumRoot, groups, MAX_LOG_BYTES, MAX_XML_BYTES } from './config.ts';
import { parseJUnit, reportStatus } from './junit.ts';
import { RunStore } from './store.ts';
import { redact } from './redact.ts';
import type { Group, Run } from './types.ts';

type Active = { run: Run; child?: ChildProcess; stop?: 'cancelled' | 'timeout'; log: string; done?: Promise<void> };
type Command = { executable: string; args: string[]; cwd: string };
type PrepareCommand = (group: Group, directory: string) => Promise<Command>;

async function prepareCommand(group: Group, directory: string): Promise<Command> {
  const reportPath = path.join(directory, 'report.xml');
  if (group.engine === 'vitest') {
    const vitest = path.join(frontendRoot, 'node_modules', 'vitest', 'vitest.mjs');
    try { await access(vitest); } catch { throw new Error('Chưa có Vitest của HSK. Chạy npm ci trong hsk-app/frontend trước.'); }
    for (const file of group.files) await access(path.join(frontendRoot, file));
    return { executable: process.execPath, args: [vitest, 'run', '--config', path.join(frontendRoot, 'vitest.config.mts'), ...group.files,
      '--reporter=default', '--reporter=junit', `--outputFile=${reportPath}`], cwd: frontendRoot };
  }
  for (const file of group.files) await access(path.join(seleniumRoot, file));
  try {
    const marker = JSON.parse(await readFile(path.join(toolRoot, 'data', 'hsk-test-server.json'), 'utf8'));
    const response = await fetch('http://127.0.0.1:3000/__hsk-test-environment', { signal: AbortSignal.timeout(3000) });
    const environment = await response.json() as { environmentId?: string };
    if (!response.ok || !marker.environmentId || environment.environmentId !== marker.environmentId) throw new Error();
  } catch { throw new Error('Chưa có môi trường HSK kiểm thử được cách ly. Cấu hình .env.hsk-test với Neon branch riêng rồi chạy npm --prefix ai-test-tool run hsk:test. Không chạy Selenium trên database website hiện tại.'); }
  try {
    const response = await fetch('http://localhost:3000/login', { signal: AbortSignal.timeout(5000), redirect: 'manual' });
    if (response.status >= 400) throw new Error(`HTTP ${response.status}`);
  } catch { throw new Error('Website HSK chưa sẵn sàng tại http://localhost:3000/login. Khởi động HSK với database kiểm thử trước khi chạy Selenium.'); }
  const localPython = path.join(toolRoot, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  return { executable: process.env.PYTHON_EXECUTABLE || (existsSync(localPython) ? localPython : 'python'),
    args: ['-m', 'pytest', ...group.files.map(file => path.join(seleniumRoot, file)), '-q', '-ra',
      `--junitxml=${reportPath}`, '-o', 'junit_family=xunit2', '-o', `cache_dir=${path.join(directory, '.pytest_cache')}`], cwd: directory };
}

export class TestRunner {
  store: RunStore;
  prepare: PrepareCommand;
  active?: Active;
  constructor(store: RunStore, prepare: PrepareCommand = prepareCommand) { this.store = store; this.prepare = prepare; }

  async start(groupId: string, timeoutSeconds?: number): Promise<Run> {
    if (this.active) throw new Error('Đang có một nhóm test chạy. Hãy đợi hoặc dừng lần chạy hiện tại.');
    const group = groups.find(g => g.id === groupId);
    if (!group) throw new Error('Nhóm test không hợp lệ.');
    const timeout = timeoutSeconds ?? group.timeoutSeconds;
    if (!Number.isInteger(timeout) || timeout < 10 || timeout > 7200) throw new Error('Giới hạn thời gian phải từ 10 đến 7200 giây.');
    const run: Run = {
      id: randomUUID(), groupId, name: group.name, engine: group.engine, source: 'execution',
      status: 'running', startedAt: new Date().toISOString(), duration: 0, timeoutSeconds: timeout,
    };
    const active: Active = { run, log: '' };
    this.active = active;
    try { await this.store.save(run); }
    catch (error) { this.active = undefined; throw error; }
    active.done = this.execute(active, group).catch(async error => {
      run.status = 'error';
      run.error = redact(`Không lưu được kết quả: ${error instanceof Error ? error.message : String(error)}`);
      console.error(run.error);
      try { await this.store.save(run); } catch { /* Lỗi ổ đĩa đã được ghi vào console. */ }
    }).finally(() => { if (this.active === active) this.active = undefined; });
    return structuredClone(run);
  }

  append(active: Active, content: string) {
    active.log = Buffer.from(active.log + content).subarray(-MAX_LOG_BYTES).toString('utf8');
  }

  async execute(active: Active, group: Group) {
    const run = active.run;
    const directory = this.store.directory(run.id);
    const reportPath = path.join(directory, 'report.xml');
    let timer: NodeJS.Timeout | undefined;
    try {
      const { executable, args, cwd } = await this.prepare(group, directory);
      if (active.stop) { run.status = active.stop; return; }
      run.command = [executable, ...args].map(arg => arg.includes(' ') ? JSON.stringify(arg) : arg).join(' ');
      await this.store.save(run);
      if (active.stop) { run.status = active.stop; run.error = 'Người dùng đã dừng trước khi thực thi test.'; return; }
      const env = { ...process.env, NO_COLOR: '1', FORCE_COLOR: '0', PYTHONUNBUFFERED: '1', PYTHONIOENCODING: 'utf-8' };
      delete (env as NodeJS.ProcessEnv).GEMINI_API_KEY;
      const child = spawn(executable, args, { cwd, env, shell: false, windowsHide: true, detached: process.platform !== 'win32', stdio: ['ignore', 'pipe', 'pipe'] });
      active.child = child;
      child.stdout?.setEncoding('utf8');
      child.stderr?.setEncoding('utf8');
      child.stdout?.on('data', chunk => this.append(active, chunk));
      child.stderr?.on('data', chunk => this.append(active, chunk));
      timer = setTimeout(() => { active.stop = 'timeout'; void this.kill(active); }, run.timeoutSeconds * 1000);
      const result = await new Promise<{ code: number | null; signal: string | null }>((resolve, reject) => {
        child.once('error', reject);
        child.once('close', (code, signal) => resolve({ code, signal }));
      });
      clearTimeout(timer);
      run.exitCode = result.code;
      let reportError: string | undefined;
      try {
        if ((await stat(reportPath)).size > MAX_XML_BYTES) throw new Error('Báo cáo XML vượt giới hạn 8 MB.');
        run.report = parseJUnit(await readFile(reportPath, 'utf8'));
        run.reportFile = 'report.xml';
      } catch (error: any) {
        reportError = error.code === 'ENOENT' ? 'Trình chạy chưa tạo báo cáo XML. Xem nhật ký để kiểm tra dependency, lỗi khởi động hoặc lỗi thu thập test.' : error.message;
      }
      if (active.stop) {
        run.status = active.stop;
        run.error = active.stop === 'timeout' ? `Đã dừng toàn bộ tiến trình test sau ${run.timeoutSeconds} giây.` : 'Người dùng đã dừng lần chạy; kết quả có thể chưa đầy đủ.';
      } else if (run.report) {
        run.status = reportStatus(run.report, result.code);
        if (run.status === 'error') run.error = run.report.warnings.join('\n') || `Trình chạy kết thúc với mã ${result.code ?? result.signal}; xem chi tiết lỗi và nhật ký.`;
      } else {
        run.status = 'error';
        run.error = reportError;
      }
    } catch (error: any) {
      run.status = active.stop ?? 'error';
      run.error = error.code === 'ENOENT' ? 'Không tìm thấy Python hoặc tệp kiểm thử. Kiểm tra PYTHON_EXECUTABLE và dependency của bộ test.' : redact(error.message || String(error));
      this.append(active, `\n${run.error}\n`);
    } finally {
      if (timer) clearTimeout(timer);
      run.finishedAt = new Date().toISOString();
      run.duration = (Date.now() - Date.parse(run.startedAt)) / 1000;
      await writeFile(path.join(directory, 'output.log'), redact(active.log), 'utf8');
      await this.store.save(run);
    }
  }

  async kill(active: Active) {
    const child = active.child;
    if (!child?.pid || child.exitCode !== null || child.signalCode !== null) return;
    if (process.platform === 'win32') {
      await new Promise<void>(resolve => {
        const killer = spawn('taskkill', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore', shell: false });
        killer.once('error', () => { child.kill(); resolve(); });
        killer.once('close', code => { if (code) child.kill(); resolve(); });
      });
    } else {
      try { process.kill(-child.pid, 'SIGKILL'); } catch { child.kill('SIGKILL'); }
    }
  }

  async cancel(id: string) {
    if (!this.active || this.active.run.id !== id) throw new Error('Lần chạy này đã kết thúc hoặc không tồn tại.');
    this.active.stop = 'cancelled';
    await this.kill(this.active);
  }
  async shutdown() {
    const active = this.active;
    if (!active) return;
    active.stop = 'cancelled';
    await this.kill(active);
    await active.done;
  }
}
