/**
 * GET /api/review
 * → Trả danh sách wordId cần ôn hôm nay (nextReview <= today) từ DB
 * → Kèm thống kê: total due, total cards
 *
 * Query params:
 *   limit (optional) — giới hạn số lượng, default 50
 */
import { NextRequest, NextResponse } from "next/server";
import { getUserIdFromRequest } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const userId = getUserIdFromRequest(req);
  if (!userId) return NextResponse.json({ error: "Chưa đăng nhập." }, { status: 401 });

  const limit = parseInt(req.nextUrl.searchParams.get("limit") ?? "50");
  const requestedDate = req.nextUrl.searchParams.get("date");
  const today = requestedDate && /^\d{4}-\d{2}-\d{2}$/.test(requestedDate)
    ? requestedDate
    : new Date().toISOString().split("T")[0];

  const [dueCards, allCards] = await prisma.$transaction([
    prisma.flashcardCard.findMany({
      where: { userId, nextReview: { lte: today } },
      orderBy: { nextReview: "asc" },
      take: limit,
      select: {
        wordId: true, easeFactor: true, interval: true,
        repetitions: true, nextReview: true, lastReview: true,
      },
    }),
    prisma.flashcardCard.findMany({
      where: { userId },
      orderBy: { updatedAt: "desc" },
      take: 100,
      select: {
        wordId: true, easeFactor: true, interval: true,
        repetitions: true, nextReview: true, lastReview: true,
      },
    }),
  ]);

  return NextResponse.json({
    today,
    dueCount: dueCards.length,
    totalCards: allCards.length,
    cards: dueCards,
    allCards,
  });
}
