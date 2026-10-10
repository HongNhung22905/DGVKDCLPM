import { NextRequest, NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/prisma";
import { signToken, makeSetCookieHeader } from "@/lib/auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as { email?: string; password?: string };
    const { email, password } = body;

    if (!email || !password) {
      return NextResponse.json({ error: "Vui lòng nhập email và mật khẩu." }, { status: 400 });
    }

    // Luôn so sánh lowercase — tìm case-insensitive qua raw SQL
    const normalizedEmail = email.toLowerCase().trim();

    // MySQL: LOWER() để tìm bất kể DB lưu hoa/thường
    const users = await prisma.$queryRaw<{ id: string; name: string; email: string; passwordHash: string }[]>`
      SELECT id, name, email, passwordHash FROM User WHERE LOWER(email) = ${normalizedEmail} LIMIT 1
    `;

    const user = users[0] ?? null;

    if (!user) {
      return NextResponse.json({ error: "Email hoặc mật khẩu không đúng." }, { status: 401 });
    }

    const valid = await bcrypt.compare(password, user.passwordHash);
    if (!valid) {
      return NextResponse.json({ error: "Email hoặc mật khẩu không đúng." }, { status: 401 });
    }

    const token = signToken({ sub: user.id, name: user.name, email: user.email });

    return NextResponse.json(
      { user: { id: user.id, name: user.name, email: user.email } },
      { headers: { "Set-Cookie": makeSetCookieHeader(token) } }
    );
  } catch (err) {
    console.error("[login]", err);
    return NextResponse.json({ error: "Lỗi server, thử lại sau." }, { status: 500 });
  }
}
