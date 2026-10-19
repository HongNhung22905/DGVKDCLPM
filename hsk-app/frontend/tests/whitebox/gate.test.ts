import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  getGateEntry,
  isLessonUnlocked,
  loadGateStore,
  recordTestResult,
} from "../../lib/hskData";

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 9, 18, 12));

  // Giả lập bộ nhớ trình duyệt riêng cho từng test.
  const memory = new Map<string, string>();

  vi.stubGlobal("window", {});
  vi.stubGlobal("localStorage", {
    getItem: (key: string) => memory.get(key) ?? null,
    setItem: (key: string, value: string) => {
      memory.set(key, String(value));
    },
    removeItem: (key: string) => {
      memory.delete(key);
    },
    clear: () => memory.clear(),
  });
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("Ngưỡng và bảo toàn kết quả kiểm tra", () => {
  it.each([
    ["WB-GATE-01", 79, false],
    ["WB-GATE-02", 80, true],
    ["WB-GATE-03", 81, true],
  ] as const)("%s: điểm %i, passed=%s", (_, score, passed) => {
    const result = recordTestResult(1, 1, score);

    expect(result).toEqual({ passed, score });

    const store = loadGateStore();
    const entry = getGateEntry(1, 1, store);

    expect(entry).toEqual({
      passed,
      score,
      attempts: 1,
      lastAttemptAt: new Date().toISOString(),
    });

    // Nhóm 2 bắt đầu từ bài 4.
    expect(isLessonUnlocked(1, 4, store)).toBe(passed);
  });

  it("WB-GATE-04: đạt 80 rồi làm lại 60 vẫn giữ quyền và điểm", () => {
    recordTestResult(1, 1, 80);

    vi.setSystemTime(new Date(2026, 9, 19, 12));

    const latestResult = recordTestResult(1, 1, 60);

    // Giá trị trả về mô tả lần làm hiện tại.
    expect(latestResult).toEqual({
      passed: false,
      score: 60,
    });

    // Dữ liệu lưu giữ thành tích tốt nhất.
    const store = loadGateStore();

    expect(getGateEntry(1, 1, store)).toEqual({
      passed: true,
      score: 80,
      attempts: 2,
      lastAttemptAt: new Date().toISOString(),
    });

    expect(isLessonUnlocked(1, 4, store)).toBe(true);
  });

  it("WB-GATE-05: từ chưa đạt lên đạt cập nhật điểm và số lần", () => {
    recordTestResult(1, 1, 79);
    recordTestResult(1, 1, 81);

    const store = loadGateStore();

    expect(getGateEntry(1, 1, store)).toEqual({
      passed: true,
      score: 81,
      attempts: 2,
      lastAttemptAt: new Date().toISOString(),
    });

    expect(isLessonUnlocked(1, 4, store)).toBe(true);
  });
});