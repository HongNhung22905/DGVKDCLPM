"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import type { Word } from "@/types/hsk";
import type { SM2Card, SM2Quality } from "@/lib/hskData";
import { sm2Update, loadProgress, saveProgress } from "@/lib/hskData";
import { useAuth } from "@/components/auth/AuthProvider";
import Link from "next/link";
import {
  Brain, CheckCircle, BookOpen, Volume2, RotateCcw,
  Zap, AlertCircle, Home, ChevronRight, Gamepad2, XCircle,
} from "lucide-react";
import ProgressBar from "@/components/ui/ProgressBar";

// ─── Palette ─────────────────────────────────────────────────────────────────
const P = {
  bg:          "#FFFBEA",
  surface:     "#FFF8D6",
  surfaceH:    "#FFF3B0",
  border:      "#E8D98A",
  borderLight: "#F0E9B8",
  text:        "#1C1408",
  textMuted:   "#78614A",
  textFaint:   "#A8956A",
};

interface ReviewCard extends SM2Card { word: Word; }
type ReviewGameMode = "meaning" | "pinyin" | "hanzi";

function shuffle<T>(items: T[]): T[] {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function getToneStyle(pinyin: string): string {
  if (/[āēīōūǖ]/.test(pinyin)) return "#C0392B";
  if (/[áéíóúǘ]/.test(pinyin)) return "#B45309";
  if (/[ǎěǐǒǔǚ]/.test(pinyin)) return "#059669";
  if (/[àèìòùǜ]/.test(pinyin)) return "#2563EB";
  return P.textFaint;
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function ReviewClient({ today }: { today: string }) {
  const { user } = useAuth();

  // Queue ban đầu — các từ cần ôn hôm nay
  const [originalCards, setOriginalCards] = useState<ReviewCard[]>([]);
  // Queue đang chạy (bao gồm từ thêm lại khi sai)
  const [queue, setQueue]   = useState<ReviewCard[]>([]);
  const [index, setIndex]   = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [phase, setPhase]   = useState<"studying" | "game" | "summary">("studying");
  // Track từng từ: đúng/sai
  const [results, setResults] = useState<Map<string, "correct" | "wrong">>(new Map());
  const [loaded, setLoaded] = useState(false);
  const [startTime] = useState(() => Date.now());

  // ─── Load cards ────────────────────────────────────────────────────────────
  useEffect(() => {
    async function load() {
      let due: SM2Card[] = [];

      if (user) {
        try {
          const res = await fetch("/api/review", { credentials: "include" });
          if (res.ok) {
            const data = await res.json() as { cards: SM2Card[] };
            due = data.cards ?? [];
          }
        } catch { /* fallback */ }
      }

      if (due.length === 0) {
        const store = loadProgress();
        due = Object.values(store).filter(c => c.nextReview <= today);
      }

      if (due.length === 0) { setLoaded(true); return; }

      // Resolve words từ JSON
      const levelSet = new Set<number>();
      for (const c of due) {
        const m = c.wordId.match(/^new-(\d+)-/);
        if (m) levelSet.add(parseInt(m[1]));
      }

      const merged = new Map<string, Word>();
      for (const lvl of Array.from(levelSet)) {
        try {
          const res = await fetch(`/data/hsk-new-${lvl}.json`);
          if (!res.ok) continue;
          const data = await res.json() as { lessons?: { words: Word[] }[] };
          const words = data.lessons?.flatMap(l => l.words) ?? [];
          for (const w of words) merged.set(w.id, w);
        } catch { /**/ }
      }

      const cards: ReviewCard[] = due
        .map(c => { const word = merged.get(c.wordId); return word ? { ...c, word } : null; })
        .filter((c): c is ReviewCard => c !== null)
        .slice(0, 50);

      setOriginalCards(cards);
      setQueue(cards);
      setLoaded(true);
    }
    void load();
  }, [today, user]);

  const playAudio = useCallback((word: Word) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utt = new SpeechSynthesisUtterance(word.simplified);
      utt.lang = "zh-CN"; utt.rate = 0.85;
      window.speechSynthesis.speak(utt);
    }
  }, []);

  // ─── Xử lý đánh giá ────────────────────────────────────────────────────────
  const handleRate = useCallback((quality: SM2Quality) => {
    const current = queue[index];
    if (!current) return;

    const updated = sm2Update(current, quality);

    // Lưu localStorage + sync DB
    const store = loadProgress();
    store[updated.wordId] = updated;
    saveProgress(store);
    if (user) {
      fetch("/api/progress/flashcard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(updated),
      }).catch(() => {});
    }

    const isCorrect = quality >= 3;

    // Cập nhật kết quả: ghi nhớ kết quả cuối cùng của mỗi từ gốc
    setResults(prev => {
      const next = new Map(prev);
      next.set(current.wordId, isCorrect ? "correct" : "wrong");
      return next;
    });

    setFlipped(false);

    if (!isCorrect) {
      // Thêm lại cuối queue (chỉ 1 lần mỗi từ)
      setQueue(prev => {
        const remaining = prev.slice(index + 1);
        const alreadyQueued = remaining.some(c => c.wordId === current.wordId);
        if (alreadyQueued) return prev;
        return [...prev, { ...updated, word: current.word }];
      });
    }

    const nextIndex = index + 1;
    // Tính lại queue.length sau setState là async → dùng closure
    setQueue(prev => {
      const newLength = isCorrect ? prev.length : prev.some((c, i) => i > index && c.wordId === current.wordId) ? prev.length : prev.length + 1;
      if (nextIndex >= newLength) {
        // Sẽ done sau khi setIndex
        setTimeout(() => setPhase("summary"), 50);
      }
      return prev;
    });

    setIndex(nextIndex);
  }, [queue, index, user]);

  // Fallback: nếu index vượt queue → done
  useEffect(() => {
    if (loaded && queue.length > 0 && index >= queue.length) {
      setPhase("summary");
      // Lưu phiên ôn tập lên DB
      if (user) {
        const total   = originalCards.length;
        const correct = Array.from(results.values()).filter(v => v === "correct").length;
        const dur     = Math.round((Date.now() - startTime) / 1000);
        fetch("/api/review/history", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            date:         today,
            totalCards:   total,
            correctCards: correct,
            score:        total > 0 ? Math.round((correct / total) * 100) : 0,
            durationSec:  dur,
          }),
        }).catch(() => {});
      }
    }
  }, [index, queue.length, loaded]);

  // ─── Render ─────────────────────────────────────────────────────────────────

  if (!loaded) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: P.bg }}>
        <div className="text-sm animate-pulse" style={{ color: P.textMuted }}>Đang tải...</div>
      </div>
    );
  }

  if (originalCards.length === 0) return <EmptyState today={today} />;

  if (phase === "game") {
    return <ReviewGame cards={originalCards} onExit={() => setPhase("studying")} />;
  }

  if (phase === "summary") {
    const wrongCards = originalCards.filter(c => results.get(c.wordId) !== "correct");
    const correctCount = originalCards.filter(c => results.get(c.wordId) === "correct").length;
    return (
      <SummaryScreen
        total={originalCards.length}
        correctCount={correctCount}
        wrongCards={wrongCards}
        today={today}
        onRestart={() => {
          setQueue([...originalCards]);
          setIndex(0);
          setFlipped(false);
          setResults(new Map());
          setPhase("studying");
        }}
        onRestartWrong={() => {
          if (wrongCards.length === 0) return;
          setQueue([...wrongCards]);
          setIndex(0);
          setFlipped(false);
          setResults(new Map());
          setPhase("studying");
        }}
        onPlayAudio={playAudio}
        onPlayGame={() => setPhase("game")}
      />
    );
  }

  const current = queue[index];
  if (!current) return null;

  // Progress: dựa trên số từ GỐC đã được đánh giá (không tính từ lặp)
  const reviewedOriginal = results.size;
  const progress = originalCards.length > 0
    ? (reviewedOriginal / originalCards.length) * 100
    : 0;

  const wrongSoFar   = Array.from(results.values()).filter(v => v === "wrong").length;
  const correctSoFar = Array.from(results.values()).filter(v => v === "correct").length;
  // Số từ còn lại trong queue gốc chưa đánh giá lần đầu
  const remaining = originalCards.length - results.size;

  return (
    <div className="min-h-screen flex flex-col" style={{ background: P.bg }}>
      {/* ── Header ── */}
      <div className="sticky top-0 z-10 border-b px-4 py-3"
        style={{ background: "rgba(255,251,234,0.97)", borderColor: P.border }}>
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Brain size={16} style={{ color: "#7C3AED" }} />
              <span className="text-sm font-semibold" style={{ color: P.text }}>Ôn tập hôm nay</span>
              <span className="text-xs" style={{ color: P.textFaint }}>{today}</span>
            </div>
            {/* % tiến độ thực tế */}
            <span className="text-sm font-bold" style={{ color: "#7C3AED" }}>
              {Math.round(progress)}%
            </span>
          </div>

          <ProgressBar value={progress} color="review" height={6} />

          <button
            onClick={() => setPhase("game")}
            className="mt-3 inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold text-white"
            style={{ background: "linear-gradient(135deg,#7C3AED,#B45309)" }}
          >
            <Gamepad2 size={14} /> Chơi game ôn từ
          </button>

          <div className="flex gap-4 mt-2 text-xs">
            <span style={{ color: "#059669" }}>✓ {correctSoFar} đúng</span>
            <span style={{ color: "#C0392B" }}>✗ {wrongSoFar} cần ôn lại</span>
            <span style={{ color: P.textFaint }}>{remaining} còn lại</span>
            <span className="ml-auto" style={{ color: P.textFaint }}>
              {reviewedOriginal}/{originalCards.length} từ
            </span>
          </div>
        </div>
      </div>

      {/* ── Flashcard ── */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-8">
        <div
          className="w-full max-w-md cursor-pointer select-none"
          style={{ perspective: "1200px", height: 340 }}
          onClick={() => setFlipped(f => !f)}
        >
          <div style={{
            position: "relative", width: "100%", height: "100%",
            transformStyle: "preserve-3d",
            transition: "transform 0.5s cubic-bezier(0.4,0.2,0.2,1)",
            transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
          }}>
            <CardFront word={current.word} onAudio={() => playAudio(current.word)} />
            <CardBack  word={current.word} card={current} />
          </div>
        </div>

        {/* Badge nếu đây là lần ôn lại */}
        {results.has(current.wordId) && (
          <div className="mt-3 flex items-center gap-1.5 text-xs px-3 py-1 rounded-full"
            style={{ background: "rgba(192,57,43,0.1)", color: "#C0392B" }}>
            <RotateCcw size={11} /> Ôn lại — từ chưa nhớ
          </div>
        )}

        {flipped ? (
          <div className="mt-5 w-full max-w-md">
            <p className="text-xs text-center mb-3" style={{ color: P.textFaint }}>
              Bạn nhớ tốt đến mức nào?
            </p>
            <div className="grid grid-cols-3 gap-2">
              {QUALITY_CONFIG.map(({ quality, label, desc, color, bg }) => (
                <button key={quality}
                  onClick={e => { e.stopPropagation(); handleRate(quality); }}
                  className="py-3 rounded-xl text-xs font-semibold transition-all active:scale-95 hover:brightness-95"
                  style={{ background: bg, color }}>
                  <p>{label}</p>
                  <p className="opacity-70 mt-0.5">{desc}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <button
            onClick={() => setFlipped(true)}
            className="mt-6 px-8 py-3 rounded-xl font-semibold text-white transition-all active:scale-95 hover:brightness-110"
            style={{ background: "linear-gradient(135deg,#7C3AED,#B45309)" }}>
            Lật thẻ
          </button>
        )}

        <p className="mt-4 text-xs" style={{ color: P.textFaint }}>
          EF: {current.easeFactor} · Interval: {current.interval}d · Lần #{current.repetitions}
        </p>
      </div>
    </div>
  );
}

// ─── Quality config ───────────────────────────────────────────────────────────
function ReviewGame({ cards, onExit }: { cards: ReviewCard[]; onExit: () => void }) {
  const [mode, setMode] = useState<ReviewGameMode | null>(null);
  const [questions, setQuestions] = useState<ReviewCard[]>([]);
  const [current, setCurrent] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [correct, setCorrect] = useState(0);
  const [done, setDone] = useState(false);
  const optionSets = useMemo(() => questions.map(question =>
    shuffle([question, ...shuffle(cards.filter(card => card.wordId !== question.wordId)).slice(0, 3)]),
  ), [questions, cards]);

  const start = (nextMode: ReviewGameMode) => {
    setMode(nextMode); setQuestions(shuffle(cards)); setCurrent(0);
    setSelectedId(null); setCorrect(0); setDone(false);
  };

  const answer = (wordId: string) => {
    if (selectedId !== null) return;
    const isCorrect = wordId === questions[current].wordId;
    setSelectedId(wordId);
    if (isCorrect) setCorrect(value => value + 1);
    window.setTimeout(() => {
      if (current + 1 >= questions.length) setDone(true);
      else { setCurrent(value => value + 1); setSelectedId(null); }
    }, 850);
  };

  if (!mode) return (
    <div className="min-h-screen px-4 py-10" style={{ background: P.bg }}>
      <div className="mx-auto max-w-xl rounded-2xl border p-6" style={{ background: P.surface, borderColor: P.border }}>
        <Gamepad2 size={42} className="mx-auto mb-3" style={{ color: "#7C3AED" }} />
        <h1 className="text-center text-2xl font-bold" style={{ color: P.text }}>Game ôn tập</h1>
        <p className="mb-6 mt-1 text-center text-sm" style={{ color: P.textMuted }}>Chơi với {cards.length} từ đang đến hạn ôn tập</p>
        <div className="space-y-3">
          {([ ["meaning", "Đoán nghĩa", "Chọn nghĩa đúng của chữ Hán"], ["pinyin", "Đoán Pinyin", "Chọn cách đọc đúng"], ["hanzi", "Đoán chữ Hán", "Chọn chữ Hán theo nghĩa"] ] as [ReviewGameMode, string, string][]).map(([key, label, desc]) => (
            <button key={key} onClick={() => start(key)} className="w-full rounded-xl border p-4 text-left hover:brightness-95" style={{ background: P.surfaceH, borderColor: P.border }}>
              <span className="font-bold" style={{ color: P.text }}>{label}</span><span className="ml-2 text-sm" style={{ color: P.textMuted }}>{desc}</span>
            </button>
          ))}
        </div>
        <button onClick={onExit} className="mt-5 w-full py-2 text-sm font-medium" style={{ color: P.textMuted }}>Quay lại thẻ ôn tập</button>
      </div>
    </div>
  );

  if (done) {
    const score = Math.round((correct / questions.length) * 100);
    return (
      <div className="min-h-screen flex items-center justify-center px-4" style={{ background: P.bg }}>
        <div className="w-full max-w-sm rounded-2xl border p-7 text-center" style={{ background: P.surface, borderColor: P.border }}>
          <Zap size={44} className="mx-auto mb-3" style={{ color: "#B45309" }} />
          <h2 className="text-2xl font-bold" style={{ color: P.text }}>Hoàn thành!</h2>
          <p className="my-5 text-4xl font-extrabold" style={{ color: score >= 80 ? "#059669" : "#B45309" }}>{score}%</p>
          <p className="mb-5 text-sm" style={{ color: P.textMuted }}>Đúng {correct}/{questions.length} câu</p>
          <button onClick={() => start(mode)} className="w-full rounded-xl py-3 font-semibold text-white" style={{ background: "#7C3AED" }}><RotateCcw size={15} className="mr-2 inline" /> Chơi lại</button>
          <button onClick={() => setMode(null)} className="mt-2 w-full rounded-xl border py-3 text-sm font-semibold" style={{ borderColor: P.border, color: P.textMuted }}>Đổi chế độ</button>
          <button onClick={onExit} className="mt-2 w-full py-2 text-sm" style={{ color: P.textFaint }}>Về ôn tập</button>
        </div>
      </div>
    );
  }

  const question = questions[current];
  const options = optionSets[current];
  const prompt = mode === "hanzi" ? (question.word.meaningVi || question.word.meaning) : question.word.simplified;
  return (
    <div className="min-h-screen px-4 py-8" style={{ background: P.bg }}><div className="mx-auto max-w-xl">
      <div className="mb-5 flex items-center justify-between text-sm" style={{ color: P.textMuted }}><button onClick={onExit}>← Thẻ ôn tập</button><span>Câu {current + 1}/{questions.length} · Đúng {correct}</span></div>
      <ProgressBar value={(current / questions.length) * 100} color="review" height={6} />
      <div className="my-6 rounded-2xl border p-8 text-center" style={{ background: P.surface, borderColor: P.border }}>
        <p className="mb-3 text-xs" style={{ color: P.textFaint }}>{mode === "meaning" ? "Từ này có nghĩa là gì?" : mode === "pinyin" ? "Pinyin đúng là gì?" : "Chữ Hán nào phù hợp?"}</p>
        <p className={mode === "hanzi" ? "text-xl font-bold" : "hanzi text-6xl font-bold"} style={{ color: P.text }}>{prompt}</p>
      </div>
      <div className="grid gap-3">{options.map(option => {
        const isAnswer = option.wordId === question.wordId; const isSelected = selectedId === option.wordId; const revealed = selectedId !== null;
        const label = mode === "meaning" ? (option.word.meaningVi || option.word.meaning) : mode === "pinyin" ? option.word.pinyin : option.word.simplified;
        return <button key={option.wordId} disabled={revealed} onClick={() => answer(option.wordId)} className="flex items-center justify-between rounded-xl border px-4 py-3 text-left font-medium" style={{ background: revealed && isAnswer ? "#DCFCE7" : revealed && isSelected ? "#FEE2E2" : P.surface, borderColor: revealed && isAnswer ? "#059669" : revealed && isSelected ? "#C0392B" : P.border, color: P.text }}>
          <span className={mode === "hanzi" ? "hanzi text-2xl" : ""}>{label}</span>{revealed && isAnswer && <CheckCircle size={17} style={{ color: "#059669" }} />}{revealed && isSelected && !isAnswer && <XCircle size={17} style={{ color: "#C0392B" }} />}
        </button>;
      })}</div>
    </div></div>
  );
}

const QUALITY_CONFIG = [
  { quality: 0 as SM2Quality, label: "Không biết", desc: "Nhắc ngay",  color: "#fff",    bg: "#C0392B" },
  { quality: 1 as SM2Quality, label: "Sai",         desc: "Sắp nhắc",  color: "#fff",    bg: "#EA580C" },
  { quality: 2 as SM2Quality, label: "Gần đúng",    desc: "Nhớ mờ",    color: "#1C1408", bg: "#FDE68A" },
  { quality: 3 as SM2Quality, label: "Đúng",        desc: "Nhớ được",  color: "#fff",    bg: "#2563EB" },
  { quality: 4 as SM2Quality, label: "Tốt",         desc: "Nhớ rõ",    color: "#fff",    bg: "#059669" },
  { quality: 5 as SM2Quality, label: "Dễ",          desc: "Nhớ ngay",  color: "#fff",    bg: "#7C3AED" },
];

// ─── Card faces ───────────────────────────────────────────────────────────────
function CardFront({ word, onAudio }: { word: Word; onAudio: () => void }) {
  return (
    <div style={{ position: "absolute", inset: 0, backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden" }}>
      <div className="rounded-2xl border w-full h-full flex flex-col items-center justify-center p-8"
        style={{ borderColor: P.border, backgroundColor: P.surface }}>
        <p className="text-xs mb-5 tracking-widest uppercase" style={{ color: P.textFaint }}>Chữ Hán</p>
        <p className="hanzi font-bold mb-4"
          style={{ fontSize: "clamp(4rem,15vw,6rem)", lineHeight: 1, color: P.text }}>
          {word.simplified}
        </p>
        <button onClick={e => { e.stopPropagation(); onAudio(); }}
          className="mb-5 transition-colors" style={{ color: P.textFaint }}
          onMouseEnter={e => (e.currentTarget as HTMLElement).style.color = "#7C3AED"}
          onMouseLeave={e => (e.currentTarget as HTMLElement).style.color = P.textFaint}>
          <Volume2 size={20} />
        </button>
        <p className="text-sm" style={{ color: P.textFaint }}>↕ Nhấn để lật</p>
      </div>
    </div>
  );
}

function CardBack({ word }: { word: Word; card: ReviewCard }) {
  return (
    <div style={{
      position: "absolute", inset: 0,
      backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden",
      transform: "rotateY(180deg)",
    }}>
      <div className="rounded-2xl border w-full h-full flex flex-col items-center justify-center p-8"
        style={{ borderColor: "#B45309", backgroundColor: P.surfaceH }}>
        <p className="hanzi text-5xl font-bold mb-1" style={{ color: P.text }}>
          {word.simplified}
        </p>
        {word.traditional && word.traditional !== word.simplified && (
          <p className="hanzi text-xl mb-1" style={{ color: P.textFaint }}>{word.traditional}</p>
        )}
        <p className="text-xl font-semibold mb-4" style={{ color: getToneStyle(word.pinyin) }}>
          {word.pinyin}
        </p>
        <div className="text-center space-y-1 max-w-xs">
          {word.meaningVi && (
            <p className="font-bold text-base mb-2" style={{ color: P.text }}>{word.meaningVi}</p>
          )}
          {word.meanings.slice(0, 3).map((m, i) => (
            <p key={i} className="text-sm leading-relaxed" style={{ color: P.textMuted }}>
              {i === 0 && <span style={{ color: "#7C3AED", marginRight: 4 }}>▶</span>}
              {m}
            </p>
          ))}
        </div>
        <p className="text-xs mt-4" style={{ color: P.textFaint }}>↕ Nhấn để lật lại</p>
      </div>
    </div>
  );
}

// ─── Summary Screen ───────────────────────────────────────────────────────────
function SummaryScreen({
  total, correctCount, wrongCards, today,
  onRestart, onRestartWrong, onPlayAudio, onPlayGame,
}: {
  total: number;
  correctCount: number;
  wrongCards: ReviewCard[];
  today: string;
  onRestart: () => void;
  onRestartWrong: () => void;
  onPlayAudio: (w: Word) => void;
  onPlayGame: () => void;
}) {
  const score      = total > 0 ? Math.round((correctCount / total) * 100) : 0;
  const wrongCount = wrongCards.length;

  return (
    <div className="min-h-[calc(100vh-48px)] px-4 py-8" style={{ background: P.bg }}>
      <div className="max-w-xl mx-auto space-y-4">

        {/* ── Breadcrumb ── */}
        <nav className="flex items-center gap-1.5 text-xs mb-2" style={{ color: P.textFaint }}>
          <Link href="/" className="flex items-center gap-1 hover:underline">
            <Home size={11} /> Trang chủ
          </Link>
          <ChevronRight size={10} />
          <span style={{ color: P.textMuted }}>Ôn tập hôm nay</span>
        </nav>

        {/* ── Score card ── */}
        <div className="rounded-2xl border p-6 text-center"
          style={{ background: P.surface, borderColor: P.border }}>
          <Zap size={40} className="mx-auto mb-3" style={{ color: "#B45309" }} />
          <h2 className="text-2xl font-extrabold mb-1" style={{ color: P.text }}>
            Ôn tập xong!
          </h2>
          <p className="text-sm mb-5" style={{ color: P.textMuted }}>
            {score >= 90 ? "Xuất sắc, bạn nhớ rất tốt! 🎉"
              : score >= 70 ? "Tốt lắm, tiếp tục duy trì nhé! 👍"
              : score >= 50 ? "Ổn đấy, ôn thêm những từ sai nhé 💪"
              : "Cần ôn thêm nhiều hơn, đừng nản nhé! 🔥"}
          </p>

          <div className="grid grid-cols-3 gap-3 mb-5">
            {[
              { v: total,          l: "Từ ôn",    c: P.text },
              { v: correctCount,   l: "Nhớ đúng", c: "#059669" },
              { v: `${score}%`,    l: "Tỉ lệ",    c: score >= 80 ? "#7C3AED" : score >= 60 ? "#B45309" : "#C0392B" },
            ].map(s => (
              <div key={s.l} className="rounded-xl p-3" style={{ background: P.surfaceH }}>
                <p className="text-2xl font-extrabold" style={{ color: s.c }}>{s.v}</p>
                <p className="text-xs mt-0.5" style={{ color: P.textFaint }}>{s.l}</p>
              </div>
            ))}
          </div>

          <div className="flex flex-col gap-2">
            <button onClick={onPlayGame}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold text-white transition-all hover:brightness-110"
              style={{ background: "linear-gradient(135deg,#7C3AED,#B45309)" }}>
              <Gamepad2 size={15} /> Chơi game với {total} từ vừa ôn
            </button>
            {wrongCount > 0 && (
              <button onClick={onRestartWrong}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold text-white transition-all hover:brightness-110"
                style={{ background: "linear-gradient(135deg,#C0392B,#E74C3C)" }}>
                <RotateCcw size={14} /> Ôn lại {wrongCount} từ chưa nhớ
              </button>
            )}
            <button onClick={onRestart}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium border transition-all"
              style={{ borderColor: P.border, color: P.textMuted, background: P.surfaceH }}>
              <RotateCcw size={13} /> Ôn lại từ đầu
            </button>
            <Link href="/vocabulary"
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold text-white transition-all hover:brightness-110"
              style={{ background: "linear-gradient(135deg,#B45309,#D97706)" }}>
              <BookOpen size={14} /> Học bài mới
            </Link>
          </div>
        </div>

        {/* ── Danh sách từ chưa nhớ ── */}
        {wrongCount > 0 && (
          <div className="rounded-2xl border overflow-hidden"
            style={{ borderColor: "rgba(192,57,43,0.3)" }}>
            <div className="px-4 py-3 flex items-center gap-2"
              style={{ background: "rgba(192,57,43,0.08)" }}>
              <AlertCircle size={15} style={{ color: "#C0392B" }} />
              <p className="text-sm font-semibold" style={{ color: "#C0392B" }}>
                {wrongCount} từ cần ôn thêm
              </p>
            </div>

            <div className="divide-y" style={{ borderColor: P.borderLight }}>
              {wrongCards.map(card => (
                <div key={card.wordId} className="px-4 py-3 flex items-center gap-3"
                  style={{ background: P.surface }}>
                  <div className="flex-1 min-w-0 flex items-center gap-3">
                    <span className="hanzi text-2xl font-bold flex-shrink-0" style={{ color: P.text }}>
                      {card.word.simplified}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium" style={{ color: getToneStyle(card.word.pinyin) }}>
                        {card.word.pinyin}
                      </p>
                      <p className="text-xs truncate" style={{ color: P.textMuted }}>
                        {card.word.meaningVi || card.word.meaning}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => onPlayAudio(card.word)}
                    className="flex-shrink-0 transition-colors"
                    style={{ color: P.textFaint }}
                    onMouseEnter={e => (e.currentTarget as HTMLElement).style.color = "#7C3AED"}
                    onMouseLeave={e => (e.currentTarget as HTMLElement).style.color = P.textFaint}
                  >
                    <Volume2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {wrongCount === 0 && (
          <div className="rounded-2xl border p-4 flex items-center gap-3"
            style={{ background: "rgba(5,150,105,0.06)", borderColor: "rgba(5,150,105,0.3)" }}>
            <CheckCircle size={20} style={{ color: "#059669" }} />
            <p className="text-sm font-semibold" style={{ color: "#059669" }}>
              Tuyệt vời! Bạn nhớ tất cả {total} từ hôm nay 🎉
            </p>
          </div>
        )}

        <p className="text-xs text-center pb-4" style={{ color: P.textFaint }}>
          {today} · SM-2 tự động lên lịch ôn tập tiếp theo
        </p>
      </div>
    </div>
  );
}

// ─── Empty State ──────────────────────────────────────────────────────────────
function EmptyState({ today }: { today: string }) {
  return (
    <div className="min-h-[calc(100vh-48px)] flex flex-col items-center justify-center px-4 py-12"
      style={{ background: P.bg }}>
      <div className="rounded-2xl border p-8 max-w-sm w-full text-center"
        style={{ borderColor: P.border, backgroundColor: P.surface }}>
        <CheckCircle size={48} className="mx-auto mb-4" style={{ color: "#059669" }} />
        <h2 className="text-2xl font-bold mb-2" style={{ color: P.text }}>Xong rồi!</h2>
        <p className="text-sm mb-6" style={{ color: P.textMuted }}>
          Không có từ nào cần ôn hôm nay ({today}).
          <br />Hãy học bài mới để thêm từ vào lịch ôn tập.
        </p>
        <Link href="/vocabulary"
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold text-white transition-all hover:brightness-110"
          style={{ background: "linear-gradient(135deg,#B45309,#D97706)" }}>
          <BookOpen size={16} /> Học bài mới
        </Link>
      </div>
    </div>
  );
}
