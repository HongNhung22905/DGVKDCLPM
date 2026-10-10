# 🀄 HSK Vocabulary App — Monorepo

Ứng dụng học từ vựng tiếng Trung theo chuẩn **HSK 3.0** (tiêu chuẩn 9 bậc 2021).  
7 cấp độ · 105 bài học · 2100 từ · nghĩa tiếng Việt · flashcard SM-2 · luyện viết · game · kiểm tra có gate · AI Tutor · ngữ pháp.

---

## 📁 Cấu trúc Monorepo

```
hsk-app/
├── frontend/          ← Next.js 14 + React + Tailwind (UI + API Routes)
│   ├── app/           ← Pages + API route handlers (Next.js App Router)
│   │   ├── api/
│   │   │   ├── auth/        ← login, logout, me
│   │   │   ├── ai/          ← examples, explain, grammar, translate (Gemini)
│   │   │   ├── progress/    ← flashcard, gate, lesson
│   │   │   └── review/      ← lịch ôn từ vựng
│   │   ├── vocabulary/      ← Từ vựng, flashcard, game, viết, kiểm tra
│   │   ├── grammar/         ← Ngữ pháp HSK
│   │   ├── ai-tutor/        ← AI Tutor chat (Gemini)
│   │   ├── review/          ← Ôn tập từ vựng
│   │   ├── progress/        ← Thống kê tiến độ học
│   │   ├── writing/         ← Luyện viết chữ Hán
│   │   ├── login/
│   │   ├── register/
│   │   ├── notebook/
│   │   └── search/
│   ├── components/    ← React components
│   │   ├── ai/        ← AiTutorClient
│   │   ├── auth/      ← AuthProvider (context), AuthButton
│   │   ├── grammar/   ← Grammar components
│   │   ├── review/    ← Review components
│   │   ├── ui/        ← BackButton, Badge, ProgressBar
│   │   └── vocabulary/← VocabularyClient, FlashcardClient, GameClient...
│   ├── lib/           ← Utilities
│   │   ├── auth.ts              ← JWT helpers (client)
│   │   ├── gemini.ts            ← Google Gemini API client
│   │   ├── grammarDataServer.ts ← Server-only: đọc dữ liệu ngữ pháp
│   │   ├── grammarDetector.ts   ← Phát hiện điểm ngữ pháp trong câu
│   │   ├── hskData.ts           ← Client-safe: SM-2, localStorage, gate system
│   │   ├── hskDataServer.ts     ← Server-only: đọc JSON bằng Node.js fs
│   │   ├── notebookData.ts      ← Sổ tay localStorage
│   │   ├── prisma.ts            ← Prisma Client singleton
│   │   └── progressStats.ts     ← Tính toán thống kê tiến độ
│   ├── types/         ← TypeScript interfaces (Word, Lesson, SM2Card...)
│   ├── public/data/   ← Dataset JSON tĩnh (hsk-new-1..7.json)
│   ├── scripts/       ← processData.mjs, translateVi.mjs
│   └── prisma/        ← Prisma Client (generate từ backend/prisma/)
│
└── backend/           ← Server utilities + DB schema
    ├── lib/
    │   ├── auth.ts    ← JWT sign/verify (jsonwebtoken)
    │   ├── prisma.ts  ← Prisma Client singleton
    │   └── session.ts ← httpOnly cookie helpers
    └── prisma/
        ├── schema.prisma ← DB schema (User, Progress, Flashcard, Gate...)
        └── seed.ts       ← Database seeder
```

---

## 🏗 Kiến trúc

```
Browser  ←──────────────────────────────────────────────────────────────►  Neon PostgreSQL
         React Components                                              Prisma ORM
         (components/)                                                 (backend/prisma/)
              ↕ fetch / API calls
         Next.js API Routes                      JWT Cookie (httpOnly)
         (frontend/app/api/)  ←── lib/auth.ts ──────────────────────────►  Session
              ↕ Prisma queries
         PostgreSQL (Neon)
              ↕
         Google Gemini API  ←── lib/gemini.ts  (AI Tutor, dịch, giải thích)
```

**Frontend** (Next.js) đảm nhận cả UI lẫn API routes. **Backend** folder chứa schema DB và server utilities được import bởi các API routes.

---

## ✨ Tính năng

| Module | Mô tả | Thuật toán |
|---|---|---|
| 📖 **Từ vựng** | 15 bài/cấp · 20 từ/bài · nghĩa EN + VI · audio TTS | — |
| ⚡ **Flashcard** | Lật thẻ · 6 mức đánh giá · lịch ôn thông minh | SM-2 |
| ✍️ **Luyện viết** | Thứ tự nét chuẩn · chế độ tự kiểm tra | Hanzi Writer |
| 🎮 **Game** | Quiz nghĩa / Pinyin / Chữ Hán · 4 đáp án | Levenshtein |
| 📝 **Kiểm tra** | 20 câu random · điền pinyin · trắc nghiệm | Levenshtein |
| 🔒 **Gate system** | Đạt ≥80% mới mở 3 bài tiếp theo | — |
| 👤 **Auth** | Đăng ký / đăng nhập · JWT httpOnly cookie | bcrypt + JWT |
| 📒 **Sổ tay** | Lưu từ yêu thích · ghi chú cá nhân | localStorage + DB |
| 🔍 **Tra từ** | Tìm theo Hán / Pinyin / nghĩa · fuzzy search | Levenshtein |
| 🤖 **AI Tutor** | Chat với Gemini · giải thích từ/câu · dịch · ví dụ | Gemini API |
| 📚 **Ngữ pháp** | Điểm ngữ pháp HSK · phát hiện trong câu | — |
| 📊 **Tiến độ** | Thống kê học tập · biểu đồ tiến độ | — |
| 🔁 **Ôn tập** | Ôn lại từ đã học theo lịch | SM-2 |

---

## 🚀 Cài đặt & chạy

### Yêu cầu
- Node.js ≥ 18 · npm ≥ 9

### Cài đặt

```bash
cd hsk-app/frontend && npm install
cd ../backend && npm install
```

### Cấu hình môi trường

```bash
cp frontend/.env.local.example frontend/.env.local
```

Các biến cần điền:
- `DATABASE_URL` — PostgreSQL connection string (Neon, Supabase, Railway...)
- `NEXTAUTH_SECRET` — JWT secret (chạy `openssl rand -base64 32` để tạo)
- `GEMINI_API_KEY` — Google Gemini API key (cho AI Tutor)

### Khởi tạo database

```bash
cd hsk-app/backend
npm install
npm run db:push
```

### Chạy development

```bash
cd frontend
npm run dev
# → http://localhost:3000
```

---

## 📊 API Endpoints

### Auth
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/auth/register` | Đăng ký tài khoản |
| POST | `/api/auth/login` | Đăng nhập |
| POST | `/api/auth/logout` | Đăng xuất |
| GET | `/api/auth/me` | Thông tin user hiện tại |

### Progress
| Method | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/api/progress/lesson` | Tiến độ bài học |
| GET/POST | `/api/progress/flashcard` | Đồng bộ SM-2 cards |
| GET/POST | `/api/progress/gate` | Kết quả kiểm tra gate |

### AI (Gemini)
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/ai/translate` | Dịch từ/câu |
| POST | `/api/ai/explain` | Giải thích từ/câu |
| POST | `/api/ai/examples` | Tạo câu ví dụ |
| POST | `/api/ai/grammar` | Phân tích ngữ pháp |

### Khác
| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/review` | Danh sách từ cần ôn tập |

---

## 🗄 Database Schema

```
User ──┬── LessonProgress  (userId + lessonId)
       ├── FlashcardCard   (userId + wordId, SM-2 fields)
       ├── GateResult      (userId + setId, passed/score)
       ├── TestResult      (userId, setId, score, history)
       ├── GameResult      (userId, lessonId, mode, score)
       └── NotebookEntry   (userId + wordId, note)
```

---

## 🔒 Gate System

```
Nhóm 1 (Bài 1–3) → Học → Kiểm tra ≥80% → Nhóm 2 mở
Nhóm 2 (Bài 4–6) → Học → Kiểm tra ≥80% → Nhóm 3 mở
...
```

Gate state lưu trong `localStorage` (`hsk_gate_v1`) và sync lên DB qua `/api/progress/gate`.

---

## 📝 License

MIT · Dữ liệu từ vựng: [CC-CEDICT](https://www.mdbg.net/chinese/dictionary) · [complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) (MIT)
