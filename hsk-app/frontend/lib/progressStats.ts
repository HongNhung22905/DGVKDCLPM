/**
 * progressStats.ts — Client-side thống kê tiến độ học
 * Đọc từ localStorage: hsk_lesson_progress, hsk_gate_v1, hsk_progress, hsk_notebook_v1
 */

import {
  loadLessonProgress, loadGateStore, loadProgress,
  type LessonProgressEntry, type GateEntry,
} from "@/lib/hskData";
import { loadNotebook } from "@/lib/notebookData";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface LevelStats {
  level: number;
  label: string;
  totalLessons: number;       // 15
  completedLessons: number;
  passedSets: number;         // số set đã pass (mỗi set 3 bài)
  totalSets: number;          // 5 (set 1-5, 15 bài)
  avgScore: number;           // điểm trung bình các bài đã làm
  bestScore: number;
  wordsLearned: number;       // số từ đã học (bài completed × 20)
  flashcardsReviewed: number; // số wordId có SM-2 data
  pct: number;                // % hoàn thành (completedLessons/15)
  accent: string;
  lastStudied?: string;       // ISO string bài gần nhất
}

export interface OverallStats {
  totalLessons: number;
  completedLessons: number;
  totalWords: number;         // 2100
  wordsLearned: number;
  flashcardsReviewed: number;
  notebookCount: number;
  avgScore: number;
  streak: number;             // ngày học liên tiếp (tính từ completedAt)
  lastStudied?: string;
  levels: LevelStats[];
}

// ─── Config ───────────────────────────────────────────────────────────────────

const LEVEL_ACCENTS: Record<number, string> = {
  1: "#FF6B6B", 2: "#60A5FA", 3: "#A78BFA",
  4: "#34D399", 5: "#F59E0B", 6: "#FB923C", 7: "#E879F9",
};

const TOTAL_LESSONS_PER_LEVEL = 15;
const WORDS_PER_LESSON        = 20;
const SETS_PER_LEVEL          = 5; // 15 bài / 3 = 5 set

// ─── Compute stats ────────────────────────────────────────────────────────────

export function computeProgressStats(): OverallStats {
  const lessonProgress = loadLessonProgress();
  const gateStore      = loadGateStore();
  const sm2Cards       = loadProgress();
  const notebook       = loadNotebook();

  // Đếm flashcard đã review ít nhất 1 lần
  const flashcardsReviewed = Object.values(sm2Cards).filter(c => c.repetitions > 0).length;
  const notebookCount      = Object.keys(notebook).length;

  const levels: LevelStats[] = [];
  let totalCompleted  = 0;
  let totalWordsLearned = 0;
  let allScores: number[] = [];
  let latestDate: string | undefined;

  for (let lv = 1; lv <= 7; lv++) {
    let completedLessons = 0;
    let scores: number[] = [];
    let lvLatest: string | undefined;
    let passedSets = 0;

    for (let ln = 1; ln <= TOTAL_LESSONS_PER_LEVEL; ln++) {
      const key   = `new-${lv}-lesson-${ln}`;
      const entry = lessonProgress[key];
      if (entry?.completed) {
        completedLessons++;
        if (entry.score !== undefined) scores.push(entry.score);
        if (entry.completedAt) {
          if (!lvLatest || entry.completedAt > lvLatest) lvLatest = entry.completedAt;
        }
      }
    }

    for (let sn = 1; sn <= SETS_PER_LEVEL; sn++) {
      const setId = `new-${lv}-set-${sn}`;
      if (gateStore[setId]?.passed) passedSets++;
    }

    const avgScore  = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
    const bestScore = scores.length > 0 ? Math.max(...scores) : 0;
    const wordsLearned = completedLessons * WORDS_PER_LESSON;

    if (lvLatest && (!latestDate || lvLatest > latestDate)) latestDate = lvLatest;

    allScores = allScores.concat(scores);
    totalCompleted    += completedLessons;
    totalWordsLearned += wordsLearned;

    levels.push({
      level: lv,
      label: `HSK ${lv}`,
      totalLessons: TOTAL_LESSONS_PER_LEVEL,
      completedLessons,
      passedSets,
      totalSets: SETS_PER_LEVEL,
      avgScore,
      bestScore,
      wordsLearned,
      flashcardsReviewed: Object.keys(sm2Cards).filter(id => id.startsWith(`new-${lv}-`)).length,
      pct: Math.round((completedLessons / TOTAL_LESSONS_PER_LEVEL) * 100),
      accent: LEVEL_ACCENTS[lv] ?? "#60A5FA",
      lastStudied: lvLatest,
    });
  }

  const overallAvg = allScores.length > 0
    ? Math.round(allScores.reduce((a, b) => a + b, 0) / allScores.length)
    : 0;

  // Tính streak: đếm ngày học liên tiếp tính đến hôm nay
  const streak = computeStreak(lessonProgress);

  return {
    totalLessons:       7 * TOTAL_LESSONS_PER_LEVEL,  // 105
    completedLessons:   totalCompleted,
    totalWords:         7 * TOTAL_LESSONS_PER_LEVEL * WORDS_PER_LESSON, // 2100
    wordsLearned:       totalWordsLearned,
    flashcardsReviewed,
    notebookCount,
    avgScore:           overallAvg,
    streak,
    lastStudied:        latestDate,
    levels,
  };
}

// ─── Streak calculator ────────────────────────────────────────────────────────

function computeStreak(progress: Record<string, LessonProgressEntry>): number {
  // Lấy tập hợp ngày đã học (theo completedAt)
  const dates = new Set<string>();
  for (const entry of Object.values(progress)) {
    if (entry.completed && entry.completedAt) {
      dates.add(entry.completedAt.split("T")[0]);
    }
  }
  if (dates.size === 0) return 0;

  const today     = new Date();
  const todayStr  = today.toISOString().split("T")[0];
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const yestStr   = yesterday.toISOString().split("T")[0];

  // Nếu hôm nay hoặc hôm qua chưa học → streak = 0
  if (!dates.has(todayStr) && !dates.has(yestStr)) return 0;

  let streak = 0;
  const cursor = new Date(dates.has(todayStr) ? todayStr : yestStr);

  while (dates.has(cursor.toISOString().split("T")[0])) {
    streak++;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}
