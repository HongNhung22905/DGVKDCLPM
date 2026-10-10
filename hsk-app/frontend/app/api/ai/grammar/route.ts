import { NextRequest, NextResponse } from "next/server";
import { generateText, PROMPTS } from "@/lib/gemini";
import { getUserIdFromRequest } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const DAILY_LIMIT = parseInt(process.env.AI_DAILY_LIMIT ?? "20");

async function checkRateLimit(ip: string): Promise<boolean> {
  // Rate limit theo IP cho unauthenticated, theo userId cho authenticated
  // Dùng AiSession count trong ngày
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const count = await prisma.aiSession.count({
    where: { input: { startsWith: `__ip__${ip}` }, createdAt: { gte: today } },
  });
  return count < DAILY_LIMIT;
}

export async function POST(req: NextRequest) {
  const userId = getUserIdFromRequest(req);
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";

  // Nếu chưa đăng nhập → giới hạn theo IP
  if (!userId) {
    const allowed = await checkRateLimit(ip);
    if (!allowed) {
      return NextResponse.json(
        { error: `Đã đạt giới hạn ${DAILY_LIMIT} lượt AI/ngày. Đăng nhập để tiếp tục.` },
        { status: 429 }
      );
    }
  }

  const { sentence } = await req.json() as { sentence?: string };
  if (!sentence?.trim())
    return NextResponse.json({ error: "Vui lòng nhập câu cần chấm." }, { status: 400 });
  if (sentence.length > 500)
    return NextResponse.json({ error: "Câu quá dài (tối đa 500 ký tự)." }, { status: 400 });

  try {
    const raw = await generateText(PROMPTS.grammar(sentence));
    const result = JSON.parse(raw.replace(/```json|```/g, "").trim());

    // Ghi log session (dùng userId hoặc IP placeholder)
    await prisma.aiSession.create({
      data: {
        userId: userId ?? `__ip__${ip}__`,
        type: "grammar",
        input: userId ? sentence : `__ip__${ip}__${sentence}`,
        output: raw,
        tokens: raw.length,
      },
    }).catch(() => {/* không block nếu user chưa có trong DB */});

    return NextResponse.json(result);
  } catch (err) {
    console.error("[ai/grammar]", err);
    const msg = err instanceof Error ? err.message : "";
    if (msg.includes("chưa được cấu hình"))
      return NextResponse.json({ error: "GEMINI_API_KEY chưa được cấu hình." }, { status: 503 });
    return NextResponse.json({ error: "Không thể kết nối AI. Thử lại sau." }, { status: 500 });
  }
}
