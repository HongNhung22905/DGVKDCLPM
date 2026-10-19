import {
  afterEach, beforeEach, describe, expect, it, vi,
} from "vitest";

import {
  createNewCard,
  getSetForLesson,
  isLessonUnlocked,
  isSetUnlocked,
  sm2Update,
  type GateStore,
  type SM2Card,
} from "../../lib/hskData";

function makeCard(overrides: Partial<SM2Card> = {}): SM2Card {
  return {
    wordId: "new-1-0",
    easeFactor: 2.5,
    interval: 6,
    repetitions: 2,
    nextReview: "2026-10-18",
    lastReview: "2026-10-12",
    ...overrides,
  };
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 9, 18, 12));
});

afterEach(() => {
  vi.useRealTimers();
});

describe("SM-2", () => {
  it("WB-SM2-01: tao the moi", () => {
    expect(createNewCard("new-1-0")).toEqual({
      wordId: "new-1-0",
      easeFactor: 2.5,
      interval: 1,
      repetitions: 0,
      nextReview: "2026-10-18",
      lastReview: "2026-10-18",
    });
  });

  it("WB-SM2-02: quality 2 dat lai chuoi nho", () => {
    expect(sm2Update(makeCard(), 2)).toEqual({
      wordId: "new-1-0",
      easeFactor: 2.18,
      interval: 1,
      repetitions: 0,
      nextReview: "2026-10-19",
      lastReview: "2026-10-18",
    });
  });

  it("WB-SM2-03: quality 3 vao nhanh nho", () => {
    expect(sm2Update(makeCard({ repetitions: 0 }), 3)).toEqual({
      wordId: "new-1-0",
      easeFactor: 2.36,
      interval: 1,
      repetitions: 1,
      nextReview: "2026-10-19",
      lastReview: "2026-10-18",
    });
  });

  it("WB-SM2-04: lan nho thu hai", () => {
    expect(sm2Update(
      makeCard({ repetitions: 1, interval: 1 }), 4,
    )).toEqual({
      wordId: "new-1-0",
      easeFactor: 2.5,
      interval: 6,
      repetitions: 2,
      nextReview: "2026-10-24",
      lastReview: "2026-10-18",
    });
  });

  it("WB-SM2-05: lan ba nhan he so cu", () => {
    expect(sm2Update(makeCard(), 5)).toEqual({
      wordId: "new-1-0",
      easeFactor: 2.6,
      interval: 15,
      repetitions: 3,
      nextReview: "2026-11-02",
      lastReview: "2026-10-18",
    });
  });

  it("WB-SM2-06: he so toi thieu", () => {
    const result = sm2Update(makeCard({ easeFactor: 1.3 }), 0);
    expect(result.easeFactor).toBe(1.3);
    expect(result.interval).toBe(1);
    expect(result.repetitions).toBe(0);
  });

  it("WB-SM2-07: lam tron khoang on", () => {
    const result = sm2Update(
      makeCard({ interval: 3, easeFactor: 2.5 }), 4,
    );
    expect(result.interval).toBe(8);
    expect(result.nextReview).toBe("2026-10-26");
  });

  it("WB-SM2-08: chuyen nam", () => {
    vi.setSystemTime(new Date(2026, 11, 31, 12));
    const result = sm2Update(makeCard({ repetitions: 0 }), 4);
    expect(result.lastReview).toBe("2026-12-31");
    expect(result.nextReview).toBe("2027-01-01");
  });

  it("WB-SM2-09: nam nhuan", () => {
    vi.setSystemTime(new Date(2028, 1, 28, 12));
    const result = sm2Update(makeCard({ repetitions: 0 }), 4);
    expect(result.nextReview).toBe("2028-02-29");
  });

  it("WB-SM2-10: giu nguyen dau vao", () => {
    const card = makeCard();
    const before = { ...card };
    const result = sm2Update(card, 5);
    expect(card).toEqual(before);
    expect(result).not.toBe(card);
  });
});

describe("Mo khoa", () => {
  const passed: GateStore = {
    "new-1-set-1": {
      passed: true,
      score: 80,
      attempts: 1,
      lastAttemptAt: "2026-10-18T05:00:00.000Z",
    },
  };

  const failed: GateStore = {
    "new-1-set-1": {
      passed: false,
      score: 79,
      attempts: 1,
      lastAttemptAt: "2026-10-18T05:00:00.000Z",
    },
  };

  it("WB-UNLOCK-01: bien bai 3 va 4", () => {
    expect(getSetForLesson(3)).toBe(1);
    expect(getSetForLesson(4)).toBe(2);
  });

  it("WB-UNLOCK-02: nhom dau luon mo", () => {
    expect(isLessonUnlocked(1, 1, {})).toBe(true);
    expect(isLessonUnlocked(1, 3, {})).toBe(true);
    expect(isSetUnlocked(1, 1, {})).toBe(true);
  });

  it("WB-UNLOCK-03: thieu ket qua thi khoa", () => {
    expect(isLessonUnlocked(1, 4, {})).toBe(false);
    expect(isSetUnlocked(1, 2, {})).toBe(false);
  });

  it("WB-UNLOCK-04: chua dat thi khoa", () => {
    expect(isLessonUnlocked(1, 4, failed)).toBe(false);
    expect(isSetUnlocked(1, 2, failed)).toBe(false);
  });

  it("WB-UNLOCK-05: dat thi mo", () => {
    expect(isLessonUnlocked(1, 4, passed)).toBe(true);
    expect(isLessonUnlocked(1, 6, passed)).toBe(true);
    expect(isSetUnlocked(1, 2, passed)).toBe(true);
  });

  it("WB-UNLOCK-06: khong lan cap HSK", () => {
    expect(isLessonUnlocked(2, 4, passed)).toBe(false);
    expect(isSetUnlocked(2, 2, passed)).toBe(false);
  });

  it("WB-UNLOCK-07: khong mo vuot nhom", () => {
    expect(isLessonUnlocked(1, 7, passed)).toBe(false);
    expect(isSetUnlocked(1, 3, passed)).toBe(false);
  });
});
