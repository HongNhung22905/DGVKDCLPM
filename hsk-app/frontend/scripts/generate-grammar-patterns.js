/**
 * Script: generate-grammar-patterns.js
 * Convert hsk-sentences-audio grammar_points.json
 * → public/data/grammar-patterns.json (dùng bởi grammarDetector.ts)
 *
 * Chạy: node scripts/generate-grammar-patterns.js
 */

const fs   = require("fs");
const path = require("path");

const SRC  = path.join(__dirname, "../../../data/hsk-sentences-audio-main/hsk-sentences-audio-main/data/grammar_points.json");
const DEST = path.join(__dirname, "../public/data/grammar-patterns.json");

// ─── Load source ──────────────────────────────────────────────────────────────
const raw    = fs.readFileSync(SRC, "utf-8");
const points = JSON.parse(raw);

// ─── Transform ────────────────────────────────────────────────────────────────
// grammarDetector.ts cần: { id, level, label, label_full, pattern, exclude, examples }
// grammar_points.json đã có đúng các field đó → chỉ cần lọc và đóng gói

const patterns = points.map(p => ({
  id:         p.id,
  level:      p.level,
  label:      p.label,
  label_full: p.label_full,
  pattern:    p.pattern  ?? null,
  exclude:    p.exclude  ?? null,
  examples:   Array.isArray(p.examples) ? p.examples : [],
}));

const output = {
  total:    patterns.length,
  note:     "Generated from hsk-sentences-audio-main/data/grammar_points.json",
  patterns,
};

// ─── Write ────────────────────────────────────────────────────────────────────
fs.writeFileSync(DEST, JSON.stringify(output, null, 2), "utf-8");

// ─── Summary ──────────────────────────────────────────────────────────────────
const byLevel = {};
for (const p of patterns) {
  byLevel[p.level] = (byLevel[p.level] || 0) + 1;
}

console.log(`✅ Generated: ${DEST}`);
console.log(`   Total patterns: ${patterns.length}`);
for (const [lv, cnt] of Object.entries(byLevel).sort()) {
  const withPattern = patterns.filter(p => p.level === Number(lv) && p.pattern).length;
  console.log(`   HSK ${lv}: ${cnt} điểm ngữ pháp (${withPattern} có regex pattern)`);
}
