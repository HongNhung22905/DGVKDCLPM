import { readFile, readdir, writeFile, copyFile } from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { toolRoot, frontendRoot } from '../src/config.ts';
import { redact } from '../src/redact.ts';
import { saveEvidence, evidenceRoot } from './evidence.ts';
import type { Run, Summary } from '../src/types.ts';

const id = process.argv[2];
if (!/^[a-f0-9-]{36}$/.test(id || '')) throw new Error('Cần run ID Selenium đã kết thúc.');
const response = await fetch(`http://localhost:4317/api/runs/${id}`);
if (!response.ok) throw new Error(`Run HTTP ${response.status}`);
const run = await response.json() as Run;
if (run.status === 'running' || !run.report) throw new Error('Lần chạy chưa có báo cáo đầy đủ.');
const directories = await readdir(evidenceRoot, { withFileTypes: true });
let artifact: string | undefined;
for (const entry of directories.filter(entry => entry.isDirectory() && entry.name.startsWith('selenium-all-'))) {
  try { const saved = JSON.parse(await readFile(path.join(evidenceRoot, entry.name, 'run.json'), 'utf8')); if (saved.id === id) artifact = path.join(evidenceRoot, entry.name); } catch { /* Chưa có bản xuất. */ }
}
if (!artifact) throw new Error('Chờ script UI xuất minh chứng xong.');
const byModule: Record<string, Summary> = {};
for (const test of run.report.cases) {
  const count = byModule[test.classname] ??= { total: 0, passed: 0, failed: 0, error: 0, skipped: 0 };
  count.total++; count[test.status]++;
}
const failures = run.report.cases.filter(test => ['failed', 'error'].includes(test.status));
const screenshotNames = (await readdir(path.join(toolRoot, 'data/runs', id))).filter(name => name.endsWith('-fail.png'));
for (const name of screenshotNames) await copyFile(path.join(toolRoot, 'data/runs', id, name), path.join(artifact, name));
const result = {
  checkedAt: new Date().toISOString(), runId: id, status: run.status, summary: run.report.summary,
  byModule, duration: run.duration, reportedTestSeconds: run.report.duration,
  artifactDirectory: path.relative(toolRoot, artifact).replaceAll('\\', '/'),
  failures: failures.map(test => ({ name: test.name, module: test.classname, status: test.status, message: redact(test.message), details: redact(test.details) })),
  failureScreenshots: screenshotNames,
  sourceSha256: Object.fromEntries(await Promise.all((await readdir(path.join(frontendRoot, '../../selenium-tests'))).filter(file => file.endsWith('.py')).map(async file => [`selenium-tests/${file}`, createHash('sha256').update(await readFile(path.join(frontendRoot, '../../selenium-tests', file))).digest('hex')]))),
  note: 'Kết quả của một lượt đầy đủ. Không cộng lượt hủy hoặc lượt nhóm nhỏ vào mẫu số 85. Không sửa assertion để thay trạng thái.',
};
await saveEvidence('selenium-full-results.json', result);
const rows = Object.entries(byModule).map(([module, count]) => `| ${module} | ${count.total} | ${count.passed} | ${count.failed} | ${count.error} | ${count.skipped} |`).join('\n');
const detail = failures.map(test => `### ${test.classname} — ${test.name}\n\nTrạng thái: ${test.status}; ${test.duration.toFixed(3)} giây.\n\n\`\`\`text\n${redact(test.message)}\n${redact(test.details)}\n\`\`\``).join('\n\n');
await writeFile(path.join(artifact, 'RESULTS.md'), `# Kết quả Selenium đầy đủ\n\nRun ID: ${id}.\n\n${run.report.summary.total} ca: ${run.report.summary.passed} PASS, ${run.report.summary.failed} FAIL, ${run.report.summary.error} ERROR, ${run.report.summary.skipped} SKIP.\n\n| Module | Tổng | PASS | FAIL | ERROR | SKIP |\n| --- | ---: | ---: | ---: | ---: | ---: |\n${rows}\n\n${detail}\n`, 'utf8');
console.log(JSON.stringify({ runId: id, summary: result.summary, failures: result.failures.map(test => ({ name: test.name, message: test.message.slice(0, 800) })), artifactDirectory: result.artifactDirectory }));
