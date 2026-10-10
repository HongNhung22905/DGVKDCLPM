"use client";

import { useState } from "react";
import Link from "next/link";
import type { GrammarLevelData, GrammarPoint } from "@/lib/grammarDataServer";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";

const P = {
  bg:          "#FFFBEA",
  surface:     "#FFF8D6",
  surfaceHover:"#FFF3B0",
  border:      "#E8D98A",
  text:        "#1C1408",
  textMuted:   "#78614A",
  textFaint:   "#A8956A",
};

const LEVEL_COLORS: Record<number, { accent: string; bg: string }> = {
  1: { accent: "#C0392B", bg: "rgba(192,57,43,0.12)" },
  2: { accent: "#2563EB", bg: "rgba(37,99,235,0.12)" },
  3: { accent: "#059669", bg: "rgba(5,150,105,0.12)" },
  4: { accent: "#B45309", bg: "rgba(180,83,9,0.12)" },
  5: { accent: "#7C3AED", bg: "rgba(124,58,237,0.12)" },
  6: { accent: "#EA580C", bg: "rgba(234,88,12,0.12)" },
};

interface Props {
  data: GrammarLevelData;
}

export default function GrammarListClient({ data }: Props) {
  const [search, setSearch] = useState("");
  const colors = LEVEL_COLORS[data.levelNumber] ?? LEVEL_COLORS[1];

  const filtered = data.points.filter((p) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      p.title.toLowerCase().includes(q) ||
      p.structures.some((s) => s.toLowerCase().includes(q)) ||
      p.usedFor.some((u) => u.toLowerCase().includes(q))
    );
  });

  return (
    <div className="min-h-[calc(100vh-48px)] px-4 py-8" style={{ background: P.bg }}>
      <div className="max-w-2xl mx-auto">
        {/* Back + header */}
        <div className="mb-6">
          <Link
            href="/grammar"
            className="inline-flex items-center gap-1 text-sm mb-4 transition-colors"
            style={{ color: P.textFaint }}
            onMouseEnter={e => (e.currentTarget as HTMLElement).style.color = P.text}
            onMouseLeave={e => (e.currentTarget as HTMLElement).style.color = P.textFaint}
          >
            <ChevronLeft size={15} /> Ngữ pháp
          </Link>
          <div className="flex items-center gap-3">
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold"
              style={{ background: colors.bg, color: colors.accent }}
            >
              {data.levelNumber}
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: P.text }}>HSK {data.levelNumber} — Ngữ pháp</h1>
              <p className="text-xs mt-0.5" style={{ color: P.textMuted }}>
                {data.totalPoints} điểm ngữ pháp · {data.totalExamples} câu ví dụ
              </p>
            </div>
          </div>
        </div>

        {/* Search */}
        <div
          className="flex items-center gap-2 rounded-xl border px-3 py-2.5 mb-5 transition-all"
          style={{ borderColor: P.border, backgroundColor: P.surface }}
          onFocusCapture={e => (e.currentTarget.style.borderColor = colors.accent)}
          onBlurCapture={e => (e.currentTarget.style.borderColor = P.border)}
        >
          <Search size={15} style={{ color: P.textFaint }} className="flex-shrink-0" />
          <input
            type="text"
            placeholder="Tìm điểm ngữ pháp..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent text-sm outline-none"
            style={{ color: P.text }}
          />
        </div>

        {/* List */}
        <div className="space-y-2">
          {filtered.map((point, idx) => (
            <GrammarPointCard
              key={point.id}
              point={point}
              index={idx + 1}
              levelNumber={data.levelNumber}
              accent={colors.accent}
            />
          ))}
          {filtered.length === 0 && (
            <p className="text-center py-12" style={{ color: P.textFaint }}>
              Không tìm thấy điểm ngữ pháp nào.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function GrammarPointCard({
  point, index, levelNumber, accent,
}: { point: GrammarPoint; index: number; levelNumber: number; accent: string }) {
  return (
    <Link
      href={`/grammar/${levelNumber}/${point.id}`}
      className="flex items-start gap-4 rounded-2xl border p-4 transition-all active:scale-[0.99] block"
      style={{ borderColor: "#E8D98A", backgroundColor: "#FFF8D6" }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLElement).style.borderColor = accent;
        (e.currentTarget as HTMLElement).style.backgroundColor = "#FFF3B0";
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLElement).style.borderColor = "#E8D98A";
        (e.currentTarget as HTMLElement).style.backgroundColor = "#FFF8D6";
      }}
    >
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5"
        style={{ backgroundColor: `${accent}18`, color: accent }}
      >
        {index}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold leading-snug" style={{ color: "#1C1408" }}>{point.title}</p>
        {point.structures.length > 0 && (
          <p className="text-xs font-mono mt-1.5 truncate" style={{ color: accent }}>
            {point.structures[0]}
          </p>
        )}
        <div className="flex flex-wrap gap-1 mt-2">
          {point.usedFor.slice(0, 2).map((u) => (
            <span
              key={u}
              className="text-[10px] px-2 py-0.5 rounded-full"
              style={{ backgroundColor: "#F0E9B8", color: "#78614A" }}
            >
              {u}
            </span>
          ))}
          <span
            className="text-[10px] px-2 py-0.5 rounded-full"
            style={{ backgroundColor: "#F5E9C0", color: "#A8956A" }}
          >
            {point.examples.length} ví dụ
          </span>
        </div>
      </div>
      <ChevronRight size={16} style={{ color: "#A8956A" }} className="flex-shrink-0 mt-1" />
    </Link>
  );
}
