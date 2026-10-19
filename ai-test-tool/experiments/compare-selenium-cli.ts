import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { frontendRoot, toolRoot, seleniumRoot } from '../src/config.ts';
import { loadTestEnvironment } from '../src/hsk-test-environment.ts';
import { parseJUnit } from '../src/junit.ts';
import { redact } from '../src/redact.ts';
import { evidenceRoot, saveEvidence } from './evidence.ts';

const config = await loadTestEnvironment();
const marker = JSON.parse(await readFile(path.join(toolRoot, 'data/hsk-test-server.json'), 'utf8'));
const envResponse = await fetch('http://127.0.0.1:3000/__hsk-test-environment');
const current = await envResponse.json() as { environmentId: string };
if (!envResponse.ok || current.environmentId !== marker.environmentId || config.branch !== marker.branch) throw new Error('Không có đúng HSK test marker.');
const toolConfig = await (await fetch('http://localhost:4317/api/config')).json() as { activeRunId?: string };
if (toolConfig.activeRunId) throw new Error('Đợi lượt UI kết thúc trước khi so sánh CLI.');
const directory = path.join(evidenceRoot, `selenium-notebook-cli-${new Date().toISOString().replace(/[:.]/g, '-')}`);
await mkdir(directory, { recursive: true });
const before = createHash('sha256').update(await readFile(path.join(frontendRoot, '.env.local'))).digest('hex');
const python = path.join(toolRoot, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const args = ['-m', 'pytest', path.join(seleniumRoot, 'test_search.py'), path.join(seleniumRoot, 'test_notebook.py'), '-q', '-ra',
  `--junitxml=${path.join(directory, 'report.xml')}`, '-o', 'junit_family=xunit2', '-o', `cache_dir=${path.join(directory, '.pytest_cache')}`];
const env = { ...process.env, NO_COLOR: '1', PYTHONIOENCODING: 'utf-8', PYTHONUNBUFFERED: '1' };
delete (env as NodeJS.ProcessEnv).GEMINI_API_KEY;
const started = performance.now();
const child = spawn(python, args, { cwd: directory, env, shell: false, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
let output = '';
child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
child.stdout.on('data', chunk => { output += chunk; }); child.stderr.on('data', chunk => { output += chunk; });
const code = await new Promise<number | null>((resolve, reject) => { child.once('error', reject); child.once('close', resolve); });
const seconds = (performance.now() - started) / 1000;
await writeFile(path.join(directory, 'output.log'), redact(output), 'utf8');
const report = parseJUnit(await readFile(path.join(directory, 'report.xml'), 'utf8'));
const ui = JSON.parse(await readFile(path.join(evidenceRoot, 'selenium-notebook-122623', 'run.json'), 'utf8'));
const select = (cases: any[]) => cases.map(({ name, classname, status }) => ({ name, classname, status })).sort((a, b) => `${a.classname}/${a.name}`.localeCompare(`${b.classname}/${b.name}`));
const comparison = {
  checkedAt: new Date().toISOString(), group: 'selenium-notebook', branch: config.branch, environmentId: marker.environmentId,
  cli: { exitCode: code, processWallSeconds: seconds, reportedTestSeconds: report.duration, summary: report.summary, artifactDirectory: path.relative(toolRoot, directory).replaceAll('\\', '/') },
  ui: { runId: ui.id, runnerWallSeconds: ui.duration, reportedTestSeconds: ui.report.duration, summary: ui.report.summary, artifactDirectory: 'experiments/2026-10-19/selenium-notebook-122623' },
  casesAndStatusesIdentical: JSON.stringify(select(report.cases)) === JSON.stringify(select(ui.report.cases)),
  websiteEnvUnchanged: before === createHash('sha256').update(await readFile(path.join(frontendRoot, '.env.local'))).digest('hex'),
  timingLimit: 'Một lượt mỗi cách; UI chạy trước CLI, cùng snapshot/branch nhưng không reset DB giữa hai lượt. Các test tạo tài khoản riêng; cache và kích thước DB có thể khác. Không đo thời gian thao tác của người dùng và không kết luận UI tăng tốc Selenium.',
};
await saveEvidence('selenium-cli-ui-comparison.json', comparison);
console.log(JSON.stringify(comparison));
if (code || !comparison.casesAndStatusesIdentical) process.exitCode = 1;
