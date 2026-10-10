/**
 * GET /api/search?q=...&level=1
 * Tìm kiếm từ vựng trong tất cả file hsk-new-{n}.json
 * Hỗ trợ: chữ Hán, pinyin (có/không dấu), nghĩa tiếng Việt/Anh
 */
import { NextRequest, NextResponse } from "next/server";
import { fetchLevelDataSync } from "@/lib/hskDataServer";
import type { Word } from "@/types/hsk";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Cache toàn bộ words vào bộ nhớ (load 1 lần)
let wordCache: Word[] | null = null;

function getAllWords(): Word[] {
  if (wordCache) return wordCache;
  const words: Word[] = [];
  for (let lvl = 1; lvl <= 7; lvl++) {
    try {
      const data = fetchLevelDataSync(lvl);
      for (const lesson of data.lessons) {
        words.push(...lesson.words);
      }
    } catch { /* level không tồn tại */ }
  }
  wordCache = words;
  return words;
}

/** Chuẩn hóa pinyin: bỏ dấu thanh, lowercase */
function normalizePinyin(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "");
}

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const q     = (searchParams.get("q") ?? "").trim();
  const level = searchParams.get("level") ?? ""; // "1"–"7" hoặc ""

  if (!q) return NextResponse.json({ results: [], total: 0 });

  const qLower    = q.toLowerCase();
  const qNoPinyin = normalizePinyin(q);

  let pool = getAllWords();

  // Lọc theo level nếu có
  if (level) {
    const lvlNum = parseInt(level);
    if (!isNaN(lvlNum)) {
      pool = pool.filter(w => w.level === `new-${lvlNum}`);
    }
  }

  // Scoring: ưu tiên khớp chính xác > bắt đầu bằng > chứa
  const scored = pool
    .map(word => {
      const simplified  = word.simplified;
      const traditional = word.traditional ?? "";
      const pinyinRaw   = word.pinyin.toLowerCase();
      const pinyinNorm  = normalizePinyin(word.pinyin);
      const meaningVi   = (word.meaningVi ?? "").toLowerCase();
      const meanings    = word.meanings.map(m => m.toLowerCase()).join(" ");
      const meaning     = word.meaning.toLowerCase();

      let score = 0;

      // Khớp chữ Hán
      if (simplified === q)              score += 100;
      else if (simplified.includes(q))   score += 60;
      else if (traditional === q)        score += 90;
      else if (traditional.includes(q))  score += 50;

      // Khớp pinyin (có dấu hoặc không dấu)
      if (pinyinRaw === qLower)           score += 80;
      else if (pinyinRaw.startsWith(qLower)) score += 55;
      else if (pinyinRaw.includes(qLower))   score += 35;
      else if (pinyinNorm === qNoPinyin)     score += 75;
      else if (pinyinNorm.startsWith(qNoPinyin)) score += 50;
      else if (pinyinNorm.includes(qNoPinyin))   score += 30;

      // Khớp nghĩa tiếng Việt
      if (meaningVi === qLower)           score += 70;
      else if (meaningVi.startsWith(qLower)) score += 45;
      else if (meaningVi.includes(qLower))   score += 25;

      // Khớp nghĩa tiếng Anh
      if (meaning === qLower)             score += 60;
      else if (meaning.includes(qLower))  score += 20;
      else if (meanings.includes(qLower)) score += 15;

      return { word, score };
    })
    .filter(x => x.score > 0)
    .sort((a, b) => b.score - a.score);

  const total   = scored.length;
  const results = scored.slice(0, 40).map(x => x.word);

  return NextResponse.json({ results, total });
}
