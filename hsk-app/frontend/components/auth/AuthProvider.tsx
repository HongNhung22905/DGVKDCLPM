"use client";

/**
 * AuthProvider — API mode
 * Gọi /api/auth/* để xác thực, lưu session trong JWT cookie (HttpOnly).
 * Trạng thái user client được đồng bộ từ /api/auth/me khi mount.
 */

import {
  createContext, useContext, useState, useCallback, useEffect,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AuthUser {
  id: string;
  name: string;
  email: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ error?: string }>;
  register: (name: string, email: string, password: string) => Promise<{ error?: string }>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

// ─── Sync localStorage data → DB sau khi đăng nhập ──────────────────────────

/**
 * Khi user đăng nhập lần đầu, đẩy toàn bộ dữ liệu còn trong localStorage
 * (SM-2 cards, lesson progress, notebook) lên DB. Fire-and-forget.
 */
async function syncLocalStorageToDB(): Promise<void> {
  if (typeof window === "undefined") return;

  // 1. SM-2 Flashcard cards
  try {
    const raw = localStorage.getItem("hsk_progress");
    if (raw) {
      const cards = Object.values(JSON.parse(raw) as Record<string, unknown>);
      if (cards.length > 0) {
        await fetch("/api/progress/flashcard/bulk", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ cards }),
        });
      }
    }
  } catch { /* ignore */ }

  // 2. Lesson progress
  try {
    const raw = localStorage.getItem("hsk_lesson_progress");
    if (raw) {
      const lp = JSON.parse(raw) as Record<string, { completed: boolean; score?: number }>;
      for (const [lessonId, entry] of Object.entries(lp)) {
        if (entry.completed) {
          fetch("/api/progress/lesson", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ lessonId, completed: true, score: entry.score ?? 0 }),
          }).catch(() => {});
        }
      }
    }
  } catch { /* ignore */ }

  // 3. Gate results
  try {
    const raw = localStorage.getItem("hsk_gate_v1");
    if (raw) {
      const gates = JSON.parse(raw) as Record<string, { passed: boolean; score: number }>;
      for (const [setId, entry] of Object.entries(gates)) {
        fetch("/api/progress/gate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ setId, passed: entry.passed, score: entry.score }),
        }).catch(() => {});
      }
    }
  } catch { /* ignore */ }

  // 4. Notebook entries
  try {
    const raw = localStorage.getItem("hsk_notebook_v1");
    if (raw) {
      const notebook = JSON.parse(raw) as Record<string, {
        wordId: string; level: string; simplified: string;
        pinyin: string; meaning: string; note: string;
      }>;
      for (const entry of Object.values(notebook)) {
        fetch("/api/user/notebook", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(entry),
        }).catch(() => {});
      }
    }
  } catch { /* ignore */ }
}

// ─── Context ──────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null);

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({
  children,
  initialUser = null,
}: {
  children: ReactNode;
  initialUser?: AuthUser | null;
}) {
  const [user, setUser]       = useState<AuthUser | null>(initialUser);
  const [loading, setLoading] = useState(!initialUser); // loading cho đến khi check xong
  const router                = useRouter();

  // Khôi phục session từ JWT cookie khi mount (gọi /api/auth/me)
  useEffect(() => {
    if (initialUser) { setLoading(false); return; }
    fetch("/api/auth/me", { credentials: "include" })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.user) setUser(data.user as AuthUser);
      })
      .catch(() => {/* offline */})
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const refresh = useCallback(async () => {
    try {
      const r = await fetch("/api/auth/me", { credentials: "include" });
      if (r.ok) {
        const data = await r.json() as { user: AuthUser };
        setUser(data.user);
      } else {
        setUser(null);
      }
    } catch { setUser(null); }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const r = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });
      const data = await r.json() as { user?: AuthUser; error?: string };
      if (!r.ok) return { error: data.error ?? "Đăng nhập thất bại." };
      if (data.user) {
        setUser(data.user);
        // Sync localStorage → DB sau 1s (tránh conflict với navigation)
        setTimeout(() => { syncLocalStorageToDB().catch(() => {}); }, 1000);
      }
      return {};
    } catch (e) {
      console.error("[login]", e);
      return { error: "Không thể kết nối server. Thử lại sau." };
    }
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    try {
      const r = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ name, email, password }),
      });
      const data = await r.json() as { user?: AuthUser; error?: string };
      if (!r.ok) return { error: data.error ?? "Đăng ký thất bại." };
      if (data.user) {
        setUser(data.user);
        // Sync localStorage → DB sau 1s
        setTimeout(() => { syncLocalStorageToDB().catch(() => {}); }, 1000);
      }
      return {};
    } catch (e) {
      console.error("[register]", e);
      return { error: "Không thể kết nối server. Thử lại sau." };
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      // Xóa JWT cookie ở server
      await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
    } catch { /* offline — vẫn clear client */ }
    setUser(null);
    router.push("/");
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
