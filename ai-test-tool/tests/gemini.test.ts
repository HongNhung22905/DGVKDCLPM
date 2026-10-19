import { test } from 'node:test';
import assert from 'node:assert/strict';
import { analyzeRun, analysisContext } from '../src/gemini.ts';
import { randomUUID } from 'node:crypto';
import type { Run } from '../src/types.ts';

const run: Run = { id: randomUUID(), groupId: 'vitest-core', name: 'lỗi', engine: 'vitest', source: 'execution', status: 'error', startedAt: new Date().toISOString(), duration: 1, timeoutSeconds: 120, error: 'ImportError' };
test('thiếu key trả hướng dẫn và không gọi mạng', async () => {
  delete process.env.GEMINI_API_KEY;
  await assert.rejects(analyzeRun(run, '', async () => { throw new Error('không được gọi'); }), /Chưa cấu hình GEMINI_API_KEY/);
});
test('chỉ gửi ngữ cảnh lỗi và lưu phản hồi phân tích, không sửa trạng thái', async () => {
  process.env.GEMINI_API_KEY = 'test-key-never-real-1234';
  process.env.GEMINI_MODEL = 'gemini-test';
  const analysis = await analyzeRun(run, 'test email abc@example.com', async (url, options) => {
    assert.match(String(url), /models\/gemini-test:generateContent$/);
    assert.equal((options?.headers as Record<string, string>)['x-goog-api-key'], process.env.GEMINI_API_KEY);
    const payload = JSON.parse(String(options?.body));
    assert.match(payload.systemInstruction.parts[0].text, /Không sinh test/);
    assert.doesNotMatch(payload.contents[0].parts[0].text, /abc@example.com/);
    return Response.json({ candidates: [{ content: { parts: [{ text: 'Kiểm tra dependency.' }] }, finishReason: 'STOP' }] });
  });
  assert.equal(analysis.explanation, 'Kiểm tra dependency.');
  assert.equal(run.status, 'error');
  delete process.env.GEMINI_API_KEY;
});
test('lỗi hạn mức được giải thích mà không trả nội dung API có thể chứa key', async () => {
  process.env.GEMINI_API_KEY = 'test-key-never-real-1234';
  await assert.rejects(analyzeRun(run, '', async () => new Response('sensitive response', { status: 429 })), /Gemini HTTP 429/);
  await assert.rejects(analyzeRun(run, '', async () => Response.json({ candidates: [] })), /không trả về nội dung/);
  delete process.env.GEMINI_API_KEY;
});
test('ẩn bí mật thông dụng và giới hạn phần cuối nhật ký gửi tới Gemini', () => {
  const context = analysisContext(run, 'a'.repeat(50000) + '\npassword=hello\nAuthorization=Bearer abc.def.ghi\nuser@example.com');
  assert.ok(context.length < 12000);
  assert.doesNotMatch(context, /hello|abc\.def\.ghi|user@example.com/);
});
