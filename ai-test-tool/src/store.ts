import { mkdir, readdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { dataRoot } from './config.ts';
import type { Run } from './types.ts';

export class RunStore {
  root: string;
  constructor(root = dataRoot) { this.root = root; }
  directory(id: string): string {
    if (!/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(id)) throw new Error('Mã lần chạy không hợp lệ.');
    return path.join(this.root, id);
  }
  async save(run: Run) {
    const directory = this.directory(run.id);
    await mkdir(directory, { recursive: true });
    const temporary = path.join(directory, `run.${randomUUID()}.tmp`);
    await writeFile(temporary, JSON.stringify(run, null, 2), 'utf8');
    await rename(temporary, path.join(directory, 'run.json'));
  }
  async get(id: string): Promise<Run | undefined> {
    try { return JSON.parse(await readFile(path.join(this.directory(id), 'run.json'), 'utf8')); }
    catch (error: any) { if (error.code === 'ENOENT') return undefined; throw error; }
  }
  async list(): Promise<Run[]> {
    await mkdir(this.root, { recursive: true });
    const entries = await readdir(this.root, { withFileTypes: true });
    const runs = await Promise.all(entries.filter(e => e.isDirectory() && /^[a-f0-9-]{36}$/i.test(e.name)).map(e => this.get(e.name).catch(() => undefined)));
    return runs.filter((run): run is Run => !!run).sort((a, b) => b.startedAt.localeCompare(a.startedAt));
  }
  async recover() {
    for (const run of await this.list()) {
      if (run.status === 'running') {
        run.status = 'interrupted';
        run.finishedAt = new Date().toISOString();
        run.error = 'Công cụ đã dừng trước khi lưu kết quả cuối cùng. Hãy chạy lại nhóm test.';
        await this.save(run);
      }
    }
  }
}
