// Kiểm tra khả năng đọc các báo cáo thật đã lưu; không chạy test HSK.
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { seleniumRoot, frontendRoot } from '../src/config.ts';
import { parseJUnit } from '../src/junit.ts';

const files = (await readdir(seleniumRoot)).filter(file => file.endsWith('.xml')).map(file => path.join(seleniumRoot, file));
files.push(path.join(frontendRoot, 'whitebox-results.xml'));
let cases = 0;
const errors: string[] = [];
for (const file of files) {
  try { cases += parseJUnit(await readFile(file, 'utf8')).summary.total; }
  catch (error: any) { errors.push(`${path.basename(file)}: ${error.message}`); }
}
console.log(JSON.stringify({ files: files.length, parsed: files.length - errors.length, cases, errors }, null, 2));
if (errors.length) process.exitCode = 1;
