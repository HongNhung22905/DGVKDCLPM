import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { parseEnv } from 'node:util';
import { randomBytes } from 'node:crypto';
import { frontendRoot, toolRoot } from './config.ts';

export const normalizeDatabaseHost = (hostname: string) => hostname.toLowerCase().replace('-pooler.', '.');

export function validateTestEnvironment(values: Record<string, string>, currentDatabaseUrls: string[] = []) {
  if (!/^hsk-test(?:-|$)/.test(values.HSK_TEST_BRANCH || '')) throw new Error('HSK_TEST_BRANCH phải là tên branch kiểm thử bắt đầu bằng hsk-test.');
  let database: URL;
  try { database = new URL(values.DATABASE_URL); } catch { throw new Error('Chưa điền DATABASE_URL của Neon branch kiểm thử vào ai-test-tool/.env.hsk-test.'); }
  if (!['postgresql:', 'postgres:'].includes(database.protocol) || !database.password || !database.hostname.endsWith('.neon.tech')) throw new Error('Cần chuỗi PostgreSQL hợp lệ của Neon branch kiểm thử.');
  const expected = (values.HSK_TEST_DATABASE_HOST || '').trim();
  if (!expected || normalizeDatabaseHost(expected) !== normalizeDatabaseHost(database.hostname)) throw new Error('HSK_TEST_DATABASE_HOST chưa khớp với hostname trong DATABASE_URL kiểm thử.');
  for (const current of currentDatabaseUrls) {
    let original: URL;
    try { original = new URL(current); } catch { throw new Error('Không đọc được kết nối HSK hiện tại để kiểm tra cách ly.'); }
    if (normalizeDatabaseHost(original.hostname) === normalizeDatabaseHost(database.hostname)) throw new Error('Từ chối sử dụng cùng endpoint database với website HSK hiện tại, kể cả URL pooled/unpooled khác nhau.');
  }
  if (!['require', 'verify-full', 'verify-ca'].includes(database.searchParams.get('sslmode') || '')) throw new Error('DATABASE_URL kiểm thử cần giữ cấu hình SSL do Neon cung cấp (sslmode=require).');
  return { branch: values.HSK_TEST_BRANCH, host: database.hostname, databaseUrl: values.DATABASE_URL, authSecret: values.NEXTAUTH_SECRET || randomBytes(32).toString('hex') };
}

export async function loadTestEnvironment() {
  let values: Record<string, string>;
  try { values = parseEnv(await readFile(path.join(toolRoot, '.env.hsk-test'), 'utf8')) as Record<string, string>; }
  catch { throw new Error('Tạo ai-test-tool/.env.hsk-test từ .env.hsk-test.example và điền kết nối Neon branch kiểm thử.'); }
  const current: string[] = [];
  for (const file of ['.env.local', '.env.development.local', '.env.development', '.env']) {
    try {
      const config = parseEnv(await readFile(path.join(frontendRoot, file), 'utf8'));
      if (config.DATABASE_URL) current.push(config.DATABASE_URL);
    } catch (error: any) { if (error.code !== 'ENOENT') throw error; }
  }
  if (process.env.DATABASE_URL) current.push(process.env.DATABASE_URL);
  return validateTestEnvironment(values, current);
}
