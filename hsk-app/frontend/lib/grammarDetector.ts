/**
 * Grammar Pattern Detector — dùng cho AI Tutor
 * Detect điểm ngữ pháp trong câu tiếng Trung bằng regex
 *
 * Data source: public/data/grammar-patterns.json
 * (merge từ hsk-sentences-audio/grammar_points.json)
 *
 * Chỉ import từ Server Components / Route Handlers (dùng fs)
 */
import path from "path";
import fs from "fs";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface GrammarPattern {
  id: string;
  level: number;
  label: string;       // tiếng Trung ngắn, VD: "能愿动词(会/能)"
  label_full: string;  // tiếng Trung đầy đủ
  pattern: string;     // regex string
  exclude: string | null;
  examples: string[];
}

export interface GrammarPatternsFile {
  total: number;
  note: string;
  patterns: GrammarPattern[];
}

export interface DetectedPoint {
  id: string;
  level: number;
  label: string;
  label_full: string;
  matchedText: string;  // phần text match trong câu
}

// ─── Load data ────────────────────────────────────────────────────────────────

let _cache: GrammarPattern[] | null = null;

function loadPatterns(): GrammarPattern[] {
  if (_cache) return _cache;
  const filePath = path.join(process.cwd(), "public", "data", "grammar-patterns.json");
  const raw = fs.readFileSync(filePath, "utf-8");
  const data = JSON.parse(raw) as GrammarPatternsFile;
  _cache = data.patterns;
  return _cache;
}

// ─── Core: detect grammar points in a sentence ───────────────────────────────

/**
 * Detect tất cả điểm ngữ pháp có trong câu `text`.
 * Trả về danh sách các điểm đã detect được (có thể rỗng).
 *
 * @param text   - Câu tiếng Trung cần phân tích
 * @param maxLevel - Giới hạn level (default: 6, tức check tất cả)
 */
export function detectGrammarPoints(
  text: string,
  maxLevel = 6
): DetectedPoint[] {
  const patterns = loadPatterns().filter(p => p.level <= maxLevel);
  const detected: DetectedPoint[] = [];

  for (const gp of patterns) {
    try {
      const re = new RegExp(gp.pattern, "u");
      const excRe = gp.exclude ? new RegExp(gp.exclude, "u") : null;

      // Có match pattern?
      const match = re.exec(text);
      if (!match) continue;

      // Không nằm trong exclude?
      if (excRe && excRe.test(text)) continue;

      detected.push({
        id: gp.id,
        level: gp.level,
        label: gp.label,
        label_full: gp.label_full,
        matchedText: match[0],
      });
    } catch {
      // Pattern lỗi → bỏ qua
    }
  }

  return detected;
}

/**
 * Detect và trả về level cao nhất của ngữ pháp trong câu.
 * Hữu ích để ước tính độ khó của câu.
 */
export function estimateGrammarLevel(text: string): number {
  const points = detectGrammarPoints(text);
  if (points.length === 0) return 0;
  return Math.max(...points.map(p => p.level));
}

/**
 * Kiểm tra câu có chứa điểm ngữ pháp của level cụ thể không.
 * Dùng cho AI tutor: "câu này dùng ngữ pháp HSK2"
 */
export function hasGrammarOfLevel(text: string, level: number): boolean {
  const patterns = loadPatterns().filter(p => p.level === level);
  for (const gp of patterns) {
    try {
      const re = new RegExp(gp.pattern, "u");
      const excRe = gp.exclude ? new RegExp(gp.exclude, "u") : null;
      if (re.test(text) && (!excRe || !excRe.test(text))) return true;
    } catch { /* skip */ }
  }
  return false;
}

/**
 * Lấy tất cả patterns (dùng để truyền vào Gemini system prompt)
 */
export function getAllPatterns(): GrammarPattern[] {
  return loadPatterns();
}

/**
 * Lấy patterns theo level
 */
export function getPatternsByLevel(level: number): GrammarPattern[] {
  return loadPatterns().filter(p => p.level === level);
}
