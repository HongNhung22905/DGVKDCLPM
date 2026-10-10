/**
 * POST /api/progress/flashcard/bulk
 * body: { cards: SM2Card[] }
 * → upsert nhiều cards 1 lúc (dùng sau session flashcard)
 */
import { NextRequest, NextResponse } from "next/server";
import { getUserIdFromRequest } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

interface SM2CardBody {
  wordId: string;
  easeFactor: number;
  interval: number;
  repetitions: number;
  nextReview: string;
  lastReview: string;
}

export async function POST(req: NextRequest) {
  const userId = getUserIdFromRequest(req);
  if (!userId) return NextResponse.json({ error: "Chưa đăng nhập." }, { status: 401 });

  try {
    const body = await req.json() as { cards: SM2CardBody[] };
    if (!Array.isArray(body.cards) || body.cards.length === 0) {
      return NextResponse.json({ error: "Không có cards." }, { status: 400 });
    }

    // Prisma không có upsertMany, dùng transaction
    const ops = body.cards.map((c) =>
      prisma.flashcardCard.upsert({
        where: { userId_wordId: { userId, wordId: c.wordId } },
        create: { userId, ...c },
        update: {
          easeFactor: c.easeFactor,
          interval: c.interval,
          repetitions: c.repetitions,
          nextReview: c.nextReview,
          lastReview: c.lastReview,
        },
      })
    );

    await prisma.$transaction(ops);
    return NextResponse.json({ ok: true, saved: body.cards.length });
  } catch (err) {
    console.error("[flashcard/bulk]", err);
    return NextResponse.json({ error: "Lỗi server." }, { status: 500 });
  }
}
