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
  const today = new Date().toISOString().split("T")[0]; // "2026-10-06"

  const [dueCards, totalCards] = await prisma.$transaction([
    prisma.flashcardCard.findMany({
      where: { userId, nextReview: { lte: today } },
      orderBy: { nextReview: "asc" },
      take: limit,
      select: {
        wordId: true, easeFactor: true, interval: true,
        repetitions: true, nextReview: true, lastReview: true,
      },
    }),
    prisma.flashcardCard.count({ where: { userId } }),
  ]);

  return NextResponse.json({
    today,
    dueCount: dueCards.length,
    totalCards,
    cards: dueCards,
  });
}
