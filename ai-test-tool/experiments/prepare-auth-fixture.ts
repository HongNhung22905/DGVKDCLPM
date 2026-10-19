import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { toolRoot } from '../src/config.ts';
import { loadTestEnvironment } from '../src/hsk-test-environment.ts';
import { saveEvidence } from './evidence.ts';

// Các test register duplicate/login/logout cũ yêu cầu sẵn tài khoản cố định.
// Chỉ tạo bằng API HSK kiểm thử, không đổi/xóa tài khoản đã tồn tại.
const config = await loadTestEnvironment();
const marker = JSON.parse(await readFile(path.join(toolRoot, 'data/hsk-test-server.json'), 'utf8'));
const server = await (await fetch('http://127.0.0.1:3000/__hsk-test-environment')).json() as { environmentId: string };
if (!marker.environmentId || marker.environmentId !== server.environmentId || config.branch !== marker.branch) throw new Error('Không có HSK kiểm thử đúng marker.');
const response = await fetch('http://127.0.0.1:3000/api/auth/register', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: AbortSignal.timeout(30000),
  body: JSON.stringify({ name: 'Selenium test fixture', email: 'selenium.09b083baae11@example.com', password: '1234567' }),
});
if (![201, 409].includes(response.status)) throw new Error(`Fixture registration HTTP ${response.status}`);
await saveEvidence('auth-fixture.json', { checkedAt: new Date().toISOString(), branch: config.branch,
  environmentId: marker.environmentId, sourceFiles: ['selenium-tests/test_register.py', 'selenium-tests/test_login.py', 'selenium-tests/test_logout.py'],
  purpose: 'Các test có sẵn cần một tài khoản cố định. Tạo dữ liệu tiền điều kiện qua API trên branch kiểm thử, không sửa test/assertion.',
  registrationStatus: response.status, outcome: response.status === 201 ? 'fixture-created' : 'fixture-already-exists-no-update',
  websiteDatabaseAccessed: false });
console.log(JSON.stringify({ fixtureStatus: response.status, branch: config.branch }));
