import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateTestEnvironment } from '../src/hsk-test-environment.ts';

const values = { HSK_TEST_BRANCH: 'hsk-test-fixture', HSK_TEST_DATABASE_HOST: 'ep-test.example.neon.tech', DATABASE_URL: 'postgresql://test:placeholder@ep-test.example.neon.tech/test?sslmode=require' };
test('môi trường HSK kiểm thử cần đủ cấu hình, không tự dùng database hiện tại', () => {
  assert.throws(() => validateTestEnvironment({}), /HSK_TEST_BRANCH/);
  assert.throws(() => validateTestEnvironment({ HSK_TEST_BRANCH: 'hsk-test' }), /DATABASE_URL/);
});
test('từ chối cùng endpoint hiện tại dù khác role, database, hoặc dùng pooler', () => {
  assert.throws(() => validateTestEnvironment(values, ['postgresql://other:placeholder@ep-test-pooler.example.neon.tech/other?sslmode=require']), /cùng endpoint/);
});
test('chấp nhận endpoint Neon khác, kiểm tra host và SSL, không sửa môi trường tiến trình', () => {
  const before = process.env.DATABASE_URL;
  const checked = validateTestEnvironment(values, ['postgresql://live:placeholder@ep-live.example.neon.tech/live?sslmode=require']);
  assert.equal(checked.host, values.HSK_TEST_DATABASE_HOST);
  assert.equal(checked.databaseUrl, values.DATABASE_URL);
  assert.equal(process.env.DATABASE_URL, before);
  assert.throws(() => validateTestEnvironment({ ...values, HSK_TEST_DATABASE_HOST: 'ep-other.example.neon.tech' }), /chưa khớp/);
  assert.throws(() => validateTestEnvironment({ ...values, DATABASE_URL: values.DATABASE_URL.replace('?sslmode=require', '') }), /SSL/);
});
