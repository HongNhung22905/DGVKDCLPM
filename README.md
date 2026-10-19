# DGKDCLPM — Đánh giá và kiểm định chất lượng phần mềm

**Đề tài:** “Kiểm thử tự động website hỗ trợ học tiếng Trung và xây dựng công cụ tích hợp AI hỗ trợ phân tích kết quả.” Đánh giá website HSK là trọng tâm; HSK Test Lab là sản phẩm hỗ trợ. Hồ sơ viết báo cáo: [bảng chốt minh chứng/phiên bản](ai-test-tool/docs/EVIDENCE-BASELINE.md), [ma trận yêu cầu–tiêu chí–test–kết quả](ai-test-tool/docs/TEST-TRACEABILITY.md), [bố cục sáu chương](ai-test-tool/docs/REPORT-OUTLINE.md).

Đối tượng đánh giá: **HSK 3.0 — Nền tảng học tiếng Trung**. Repository tập hợp ứng dụng và các bằng chứng kiểm thử phục vụ đánh giá chất lượng phần mềm.

Ứng dụng web học tiếng Trung dành cho người Việt, xây dựng theo định hướng HSK 3.0. Hệ thống kết hợp học từ vựng, luyện viết chữ Hán, ngữ pháp, ôn tập ngắt quãng, đọc hiểu, hội thoại, luyện thi và gia sư AI trong một sản phẩm duy nhất.

Ứng dụng: [hsk-app-sage.vercel.app](https://hsk-app-sage.vercel.app/)

## Công cụ AI hỗ trợ kiểm thử — cập nhật 19/10/2026

Đã phát triển [HSK Test Lab](ai-test-tool/README.md): giao diện local chọn/chạy các test Vitest và Selenium có sẵn, nhập/đọc JUnit XML, hiển thị kết quả, lưu lịch sử và dùng Gemini giải thích lỗi. Phạm vi hiện tại không gồm AI sinh test hoặc đánh giá assertion.

Xem [báo cáo yêu cầu, thiết kế và thực nghiệm](ai-test-tool/docs/EXPERIMENT-REPORT.md) và [bộ minh chứng](ai-test-tool/experiments/README.md). Key Gemini mới đã gọi thành công; công cụ hiện có 21/21 test đạt. Cặp lượt Vitest bằng lệnh/UI đều 22/22 PASS, đối chiếu từng ca với XML gốc thống nhất. 70 XML là báo cáo lịch sử được kiểm tra khả năng nhập, không phải 70 lần chạy mới.

Đã chạy đủ **85 ca Selenium trên endpoint Neon kiểm thử riêng: 75 PASS, 10 FAIL**, không có ERROR/SKIP; runner khoảng 28 phút 48 giây. Nhóm tra từ/sổ tay chạy riêng bằng UI và CLI đều 10/10 PASS; NOTE-04 thất bại trong lượt đầy đủ nên chưa ổn định. [Báo cáo Selenium và minh chứng](ai-test-tool/docs/SELENIUM-RESULTS.md) phân biệt lỗi chức năng với lỗi tương tác tự động hóa; 85/85 ca hiển thị trong lịch sử khớp XML gốc. Kết nối database website hiện tại được giữ nguyên. Các phần kiểm định HSK bên dưới là tài liệu baseline trước đợt thực nghiệm mới; dùng báo cáo liên kết trên để xem trạng thái mới nhất.

Cập nhật tài liệu **20/10/2026**, không chạy test mới: [ma trận truy vết](ai-test-tool/docs/TEST-TRACEABILITY.md), [bảng 4 nhóm lỗi HSK đang mở và lỗi launcher đã sửa](ai-test-tool/docs/DEFECT-REGISTER.md), [kết luận theo tiêu chí và phạm vi chưa kiểm thử](ai-test-tool/docs/EXPERIMENT-REPORT.md#8-kết-luận-chất-lượng-theo-tiêu-chí-và-phạm-vi-chưa-kiểm-thử). Đánh giá AI trên 10 mẫu vẫn là **sơ bộ: 7 đúng, 3 đúng một phần**, chưa có người chấm độc lập và không phải độ chính xác chung 70%; [phiếu độc lập](ai-test-tool/docs/AI-INDEPENDENT-REVIEW.md) chưa có điểm.

## Đánh giá và kiểm định chất lượng phần mềm

### Mục tiêu và phạm vi

Repository phục vụ đánh giá chất lượng ứng dụng HSK 3.0 thông qua rà soát mã nguồn, kiểm thử tự động và đối chiếu kết quả với hành vi mong đợi. Phạm vi hiện có tập trung vào xác thực, học từ vựng, flashcard, ôn tập SM-2, tiến độ, thống kê, sổ tay và tính nhất quán của dữ liệu.

Thông tin dưới đây được rà soát trên nhánh `main`, tại commit `87aeadbbee552b65503b537fd2c05bfac6714cba`. Lần cập nhật tài liệu này **chưa chạy lại các bộ test**, nên chưa kết luận phiên bản hiện tại đạt các tiêu chí chất lượng.

### Các loại kiểm thử hiện có

| Nhóm kiểm thử | Công cụ và phạm vi thực tế | Mã nguồn / quy mô |
| --- | --- | --- |
| Chức năng giao diện và luồng đầu cuối (E2E) | Python, pytest, Selenium WebDriver và Chrome; thao tác qua trình duyệt, một số ca đối chiếu thêm API và trạng thái lưu trữ | [selenium-tests/](selenium-tests/): 33 file Python, 42 hàm `test_*`; nhiều hàm được tham số hóa thành nhiều ca chạy |
| Hồi quy với I/O giả lập | Node.js test runner, TypeScript; thực thi mã route/component với database, auth và React hooks được giả lập | [learning-progress-regression.test.ts](hsk-app/tests/learning-progress-regression.test.ts): 6 test |
| Kiểm tra schema và cấu hình build | Đọc schema, kiểm tra model/field, tham chiếu schema trong build và gọi `prisma generate` | [bug-condition-exploration.test.ts](hsk-app/tests/bug-condition-exploration.test.ts): 6 test |
| Tích hợp database và kiểm thử dựa trên thuộc tính (property-based) | Node.js test runner, Prisma, bcryptjs và fast-check; tạo, đọc, cập nhật, xóa dữ liệu trên PostgreSQL thật | [preservation-properties.test.ts](hsk-app/tests/preservation-properties.test.ts): 6 thuộc tính, cấu hình 10 lượt sinh đầu vào cho mỗi thuộc tính |
| Kiểm tra dữ liệu học tập | Kiểm tra số lượng, ID trùng, trường bắt buộc, phạm vi từ vựng, cấu trúc câu hỏi, chỉ số đáp án và phân bố đáp án HSK 1–2 | [validateLearningData.mjs](hsk-app/frontend/scripts/validateLearningData.mjs), [validateHsk2Data.mjs](hsk-app/frontend/scripts/validateHsk2Data.mjs) |
| Phân tích tĩnh và xác minh build | ESLint, TypeScript và production build để phát hiện lỗi mã nguồn, kiểu dữ liệu và đóng gói | [frontend/package.json](hsk-app/frontend/package.json): `npm run lint`, `npx tsc --noEmit`, `npm run build` |

Các nhóm trên có thể giao nhau: một ca Selenium vừa kiểm tra chức năng, vừa kiểm tra hồi quy hoặc giá trị biên. Số file, số hàm, số thuộc tính và số lượt sinh dữ liệu không đồng nghĩa với tổng số ca chạy hoặc tỷ lệ bao phủ mã nguồn.

### Ma trận chức năng và bằng chứng kiểm thử

| Chức năng / rủi ro | Hành vi được kiểm tra | Bằng chứng |
| --- | --- | --- |
| Đăng ký, đăng nhập, đăng xuất | Thông tin hợp lệ/sai, email trùng, trường không hợp lệ, cookie HttpOnly và trạng thái đăng xuất | [test_register.py](selenium-tests/test_register.py), [test_login.py](selenium-tests/test_login.py), [test_logout.py](selenium-tests/test_logout.py) |
| Từ vựng và flashcard | Chọn cấp HSK, khóa bài ban đầu, điều hướng từ, thao tác học flashcard | [test_vocabulary.py](selenium-tests/test_vocabulary.py), [test_flashcard.py](selenium-tests/test_flashcard.py) |
| Game và mở khóa nhóm bài | Trả lời đúng/sai, điểm số, chế độ chữ Hán/pinyin, thử lại và khôi phục mở khóa trong trình duyệt mới | [test_game.py](selenium-tests/test_game.py), [test_unlock_score.py](selenium-tests/test_unlock_score.py), [test_unlock_retry.py](selenium-tests/test_unlock_retry.py), [test_unlock_session.py](selenium-tests/test_unlock_session.py) |
| Ôn tập và lịch sử | Thẻ đến hạn/chưa đến hạn, đánh giá thẻ, ôn lặp lại và lưu lịch sử phiên một lần | [test_review_due.py](selenium-tests/test_review_due.py), [test_review_future.py](selenium-tests/test_review_future.py), [test_review_history.py](selenium-tests/test_review_history.py) |
| Luyện viết | Chế độ luyện viết, nét sai không được tính hoàn thành và hoàn thành một chữ | [test_writing.py](selenium-tests/test_writing.py), [test_writing_quiz.py](selenium-tests/test_writing_quiz.py), [test_writing_complete.py](selenium-tests/test_writing_complete.py) |
| Tiến độ, thống kê và cách ly tài khoản | Tài khoản mới, tiến độ sau học, lịch thống kê, lưu qua tải lại/đăng nhập và dữ liệu không lẫn giữa tài khoản | [test_progress_completed.py](selenium-tests/test_progress_completed.py), [test_stats_calendar.py](selenium-tests/test_stats_calendar.py), [test_stats_persistence.py](selenium-tests/test_stats_persistence.py), [test_data_isolation.py](selenium-tests/test_data_isolation.py) |
| Tra từ và sổ tay | Luồng tìm kiếm và thao tác sổ tay | [test_search.py](selenium-tests/test_search.py), [test_notebook.py](selenium-tests/test_notebook.py) |
| Lưu trữ và đồng bộ | CRUD các model, giữ lịch flashcard khi import, khôi phục tiến độ và xử lý ngày học | [preservation-properties.test.ts](hsk-app/tests/preservation-properties.test.ts), [learning-progress-regression.test.ts](hsk-app/tests/learning-progress-regression.test.ts) |

Ví dụ kỹ thuật thiết kế ca kiểm thử đang có:

- **Phân vùng tương đương:** đăng nhập đúng/sai thông tin; email đã đăng ký/chưa đăng ký; tài khoản mới/đã có dữ liệu.
- **Giá trị biên:** mật khẩu 5, 6 và 7 ký tự; điểm mở khóa 15, 16 và 17 câu đúng trên tổng 20 câu.
- **Chuyển trạng thái:** đăng nhập → đăng xuất; học → ôn tập → lưu lịch sử; chưa mở khóa → mở khóa → thử lại → khôi phục phiên.
- **Kiểm tra bảo vệ dữ liệu ở phạm vi hiện có:** cookie HttpOnly và cách ly dữ liệu tài khoản. Các ca này chưa đủ để kết luận an toàn bảo mật toàn hệ thống.

### Môi trường và cách chạy

Cài các dependency Node.js theo phần cài đặt bên dưới. Các test tích hợp cần `DATABASE_URL` trỏ tới **database kiểm thử riêng**, schema đã được khởi tạo và Prisma Client đã được sinh. Cấu hình biến môi trường cho tiến trình chạy test; không mặc định rằng Node.js test runner sẽ tự đọc `frontend/.env.local`. Test tích hợp tạo/xóa bản ghi và test schema có gọi `prisma generate`.

Chạy từ thư mục gốc repository:

```bash
# Các bộ TypeScript trong hsk-app/tests
npm --prefix hsk-app test

# Chạy riêng từng bộ
npm --prefix hsk-app run test:bug-condition
npm --prefix hsk-app run test:preservation

# Hồi quy với mock, không cần kết nối database thật
cd hsk-app
node --import tsx --test tests/learning-progress-regression.test.ts
```

`npm test` trong `hsk-app` chỉ chạy các file TypeScript của thư mục `tests`; Selenium và kiểm tra dữ liệu cần chạy riêng.

Để chạy Selenium, cài Python, Chrome, pytest và selenium. Repository hiện chưa có file dependency Python khóa phiên bản. Khởi động ứng dụng trong một terminal riêng:

```bash
# Từ gốc repository
npm --prefix hsk-app/frontend run dev
```

Sau khi ứng dụng sẵn sàng tại `http://localhost:3000`, mở terminal khác tại gốc repository:

```bash
python -m pip install pytest selenium

# Xem các ca sẽ được thu thập, chưa thực thi test
python -m pytest selenium-tests --collect-only -q

# Chạy các ca E2E và xuất báo cáo JUnit XML
python -m pytest selenium-tests --junitxml=selenium-results.xml
```

Các test hiện dùng `webdriver.Chrome()` với cửa sổ trình duyệt và URL localhost trong mã nguồn. Luồng đăng ký, học và ôn tập có thể tạo dữ liệu kiểm thử; cần chạy ứng dụng với database kiểm thử.

Kiểm tra dữ liệu và mã nguồn trong `hsk-app/frontend`:

```bash
npm run data:validate
npm run lint
npx tsc --noEmit
npm run build
```

### Ghi nhận kết quả và tiêu chí đánh giá

Mỗi lần kiểm định cần lưu commit được kiểm tra, thời điểm chạy, môi trường, phiên bản công cụ, lệnh chạy, số ca pass/fail/skip và minh chứng lỗi. Ca không chạy được do môi trường phải được ghi rõ; không tính là ca đã đạt.

| Tiêu chí đề xuất cho một đợt kiểm định | Bằng chứng cần thu thập |
| --- | --- |
| Các luồng chức năng trong phạm vi đáp ứng kết quả mong đợi | Báo cáo E2E, assertion và ảnh chụp khi lỗi |
| Thay đổi không làm hỏng hành vi đã được kiểm thử | Kết quả bộ hồi quy và preservation trên cùng commit |
| Schema và dữ liệu kiểm thử hợp lệ | Kết quả bộ schema, `data:validate` và test tích hợp |
| Mã nguồn vượt qua kiểm tra tĩnh và build | Log ESLint, TypeScript và production build |
| Các ca bảo vệ dữ liệu hiện có đạt | Kết quả kiểm tra cookie và cách ly tài khoản; ghi rõ giới hạn phạm vi |

Đây là tiêu chí đề xuất cho dự án, chưa phải kết quả nghiệm thu hoặc chứng nhận chất lượng.

Các báo cáo đã lưu trong repository:

- [BUG-CONDITION-RESULTS.md](hsk-app/tests/BUG-CONDITION-RESULTS.md): ghi nhận 5 test fail và 1 test pass trên mã trước khi sửa lỗi schema; tài liệu mô tả đây là lỗi kỳ vọng để xác nhận bug.
- [PRESERVATION-TEST-RESULTS.md](hsk-app/tests/PRESERVATION-TEST-RESULTS.md): ghi nhận 6 thuộc tính pass ở thời điểm thiết lập baseline trước khi sửa.
- [selenium-tests/](selenium-tests/): chứa báo cáo XML và ảnh chụp của các lần chạy trước, bao gồm cả lần chạy lại. Cần đối chiếu từng lần chạy với commit/môi trường; không cộng tất cả báo cáo thành một kết quả chung.

Những minh chứng lịch sử này **không xác nhận trạng thái pass/fail của phiên bản hiện tại**. Lần cập nhật README này chỉ rà soát và mô tả bộ kiểm thử.

### Giới hạn hiện tại và hướng bổ sung

- Chưa thấy cấu hình CI tự động chạy test trong `.github/workflows` hoặc cấu hình đo code coverage; chưa có tỷ lệ bao phủ được xác nhận.
- Chưa thấy bộ kiểm thử riêng cho hiệu năng/tải, accessibility hoặc chạy trên nhiều trình duyệt; bộ Selenium hiện dùng Chrome.
- Chưa thấy bộ kiểm thử bảo mật chuyên biệt. Kiểm tra cookie và cách ly tài khoản chỉ phản ánh một phần yêu cầu bảo vệ dữ liệu.
- Test preservation về AI kiểm tra lưu trữ `AiSession`; chưa kiểm tra chất lượng câu trả lời hoặc luồng Gemini thực tế.
- Kiểm tra dữ liệu HSK 1–2 không thay thế kiểm thử giao diện/đầu cuối cho chủ đề, đọc hiểu, hội thoại, phát âm và luyện thi.
- Nên bổ sung cấu hình môi trường test có thể tái lập, dependency Python khóa phiên bản, báo cáo gắn với commit, CI và phép đo coverage trước khi công bố mức chất lượng tổng thể.

## Tính năng chính

### Học từ vựng

- Từ vựng được chia theo cấp độ HSK và bài học.
- Flashcard tự động phát âm tiếng Trung.
- Đánh dấu `Thuộc` / `Chưa thuộc` và ưu tiên ôn lại từ chưa nhớ.
- Game chọn đáp án và điền chữ Hán theo nghĩa.
- Bài kiểm tra mở khóa nhóm bài tiếp theo.
- Lưu từ yêu thích và ghi chú trong Sổ tay.

### Ôn tập và tiến độ

- Lập lịch ôn theo thuật toán SM-2.
- Hiển thị từ đến hạn ôn và lịch sử phiên ôn.
- Thống kê số thẻ, điểm, chuỗi ngày học và tiến độ bài học.
- Tiến độ được lưu theo tài khoản trên PostgreSQL.
- Dữ liệu khi chưa đăng nhập được giữ trong `localStorage` và đồng bộ sau khi đăng nhập.

### Luyện viết chữ Hán

- Hiển thị thứ tự nét bằng Hanzi Writer.
- Chế độ tập viết tự động phát hoạt ảnh thứ tự nét.
- Chế độ kiểm tra chuyển thẳng sang tự viết và kiểm tra nét.

### Nội dung luyện tập mở rộng

- Từ vựng theo chủ đề với flashcard và câu hỏi kiểm tra.
- Bài đọc hiểu có pinyin, bản dịch, từ khóa và câu hỏi.
- Hội thoại theo tình huống, nghe từng câu và luyện phản xạ.
- Luyện phát âm Pinyin theo thanh điệu với âm thanh WAV chuẩn hóa.
- Đề luyện thi có đồng hồ, phiếu trả lời, chấm điểm và giải thích.
- Tiến độ của bốn module trên được đồng bộ theo tài khoản.

### Tra từ và Gia sư AI

- Tra cứu hơn 10.000 mục từ theo chữ Hán, pinyin, nghĩa tiếng Anh hoặc tiếng Việt.
- Lọc theo cấp HSK, xem từ loại, bộ thủ và nghe phát âm.
- Gia sư AI hỗ trợ dịch, giải thích, tạo ví dụ và phân tích ngữ pháp.
- Tự động thử model Gemini dự phòng khi model chính không khả dụng.

## Công nghệ

| Thành phần | Công nghệ |
| --- | --- |
| Giao diện và API | Next.js 14, React 18, TypeScript |
| CSS | Tailwind CSS |
| Cơ sở dữ liệu | PostgreSQL trên Neon |
| ORM | Prisma 5 |
| Xác thực | JWT trong cookie HttpOnly, bcryptjs |
| AI | Google Gemini API |
| Viết chữ Hán | Hanzi Writer |
| Icon | Lucide React |
| Triển khai | Vercel |

## Kiến trúc tổng thể

```text
Trình duyệt
├── Next.js pages và React components
├── localStorage (chế độ khách và bộ nhớ đệm)
└── Next.js API Routes
    ├── JWT authentication
    ├── Prisma ORM ──> Neon PostgreSQL
    └── Gemini API
```

```text
hsk-app/
├── frontend/
│   ├── app/                 # Trang và API Routes
│   ├── components/          # Component giao diện
│   ├── lib/                 # Auth, Prisma, dữ liệu và thuật toán
│   ├── public/data/         # Dữ liệu HSK và chỉ mục tra cứu
│   └── scripts/             # Xử lý, sinh và kiểm tra dữ liệu
├── backend/
│   └── prisma/
│       └── schema.prisma    # Schema PostgreSQL dùng chung
└── tests/                   # Kiểm thử cấp repository
```

`frontend` là ứng dụng chạy thực tế, đảm nhiệm cả giao diện lẫn backend qua Next.js Route Handlers. Thư mục `backend` hiện chứa schema Prisma và tiện ích cơ sở dữ liệu, không phải server cần chạy riêng.

## Các trang chính

| Đường dẫn | Chức năng |
| --- | --- |
| `/vocabulary` | Giáo trình và bài học từ vựng |
| `/review` | Ôn tập từ theo lịch SM-2 |
| `/writing` | Luyện viết chữ Hán |
| `/grammar` | Học và luyện ngữ pháp |
| `/search` | Tra từ điển |
| `/notebook` | Sổ tay cá nhân |
| `/topics` | Từ vựng theo chủ đề |
| `/reading` | Đọc hiểu |
| `/dialogues` | Hội thoại tình huống |
| `/pronunciation` | Luyện phát âm Pinyin và thanh điệu |
| `/exams` | Đề luyện thi |
| `/ai-tutor` | Gia sư AI |
| `/progress` | Tiến độ bài học |
| `/stats` | Thống kê ôn tập |

## Cài đặt local

Yêu cầu Node.js 18 trở lên, npm và một PostgreSQL database.

```bash
git clone https://github.com/buiquanghuy2005/DGKDCLPM.git
cd DGKDCLPM/hsk-app
npm install
cd frontend && npm install
cd ../backend && npm install
```

Tạo `hsk-app/frontend/.env.local` dựa trên `.env.local.example`:

```env
DATABASE_URL="postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
NEXTAUTH_SECRET="mot-chuoi-bi-mat-dai-va-ngau-nhien"
GEMINI_API_KEY="google-gemini-api-key"
AI_DAILY_LIMIT="20"
```

- `DATABASE_URL`: chuỗi kết nối PostgreSQL, bắt buộc cho đăng nhập và lưu tiến độ.
- `NEXTAUTH_SECRET`: khóa ký JWT, bắt buộc trong production.
- `GEMINI_API_KEY`: bắt buộc nếu sử dụng Gia sư AI.
- `AI_DAILY_LIMIT`: giới hạn lượt gọi AI theo ngày, mặc định là `20`.
- `GEMINI_MODELS`: tùy chọn, danh sách model dự phòng phân cách bằng dấu phẩy.

Khởi tạo schema database:

```bash
cd hsk-app/backend
npx prisma db push
```

Chạy ứng dụng:

```bash
cd ../frontend
npm run dev
```

Mở [http://localhost:3000](http://localhost:3000).

## Lệnh phát triển

Chạy trong `hsk-app/frontend`:

```bash
npm run dev             # Development server
npm run build           # Prisma generate và production build
npm run start           # Chạy production server đã build
npm run data:validate   # Kiểm tra dữ liệu học tập HSK 1 và HSK 2
npm run prisma:generate # Sinh và đồng bộ Prisma Client
npx tsc --noEmit        # Kiểm tra TypeScript
```

Chạy các bộ kiểm thử TypeScript trong `hsk-app` (Selenium và kiểm tra dữ liệu chạy riêng theo hướng dẫn ở trên):

```bash
npm test
```

## API chính

| Nhóm | Endpoint |
| --- | --- |
| Xác thực | `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` |
| Bài học | `GET/POST /api/progress/lesson`, `GET/POST /api/progress/gate` |
| Flashcard | `GET/POST /api/progress/flashcard`, `POST /api/progress/flashcard/bulk` |
| Module mới | `GET/POST /api/progress/modules` |
| Ngữ pháp | `GET/POST /api/progress/grammar` |
| Ôn tập | `GET /api/review`, `GET /api/review/history` |
| Sổ tay | `GET/POST /api/user/notebook` |
| Tra từ | `GET /api/search` |
| Gia sư AI | `POST /api/ai/translate`, `/explain`, `/examples`, `/grammar` |

Các endpoint dữ liệu cá nhân yêu cầu JWT hợp lệ trong cookie HttpOnly.

## Mô hình dữ liệu

- `User`: tài khoản người dùng.
- `LessonProgress`: bài từ vựng đã hoàn thành và điểm cao nhất.
- `FlashcardCard`: trạng thái SM-2 của từng từ.
- `GateResult`, `TestResult`, `GameResult`: kết quả kiểm tra và game.
- `NotebookEntry`: từ đã lưu và ghi chú cá nhân.
- `GrammarProgress`: điểm luyện ngữ pháp.
- `ReviewSession`: lịch sử phiên ôn tập.
- `WrongWord`: các từ người học thường trả lời sai.
- `ModuleProgress`: tiến độ chủ đề, đọc hiểu, hội thoại và luyện thi.
- `AiSession`: lịch sử yêu cầu AI khi được ghi nhận.

## Triển khai Vercel

1. Import repository `buiquanghuy2005/DGKDCLPM`.
2. Đặt **Root Directory** là `hsk-app/frontend`.
3. Framework Preset chọn **Next.js**.
4. Build Command giữ mặc định `npm run build`.
5. Khai báo `DATABASE_URL`, `NEXTAUTH_SECRET`, `GEMINI_API_KEY` và tùy chọn `AI_DAILY_LIMIT`.
6. Trước khi deploy thay đổi schema, chạy `npx prisma db push` trong `hsk-app/backend` với đúng database production.

Không đặt Root Directory thành `frontend`, vì thư mục này nằm bên trong `hsk-app`.

## Nguồn dữ liệu và giấy phép

Dự án sử dụng dữ liệu từ [CC-CEDICT](https://www.mdbg.net/chinese/dictionary) và [complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary). Hãy kiểm tra giấy phép của từng nguồn trước khi phân phối lại dữ liệu.

Mã nguồn dự án được phát hành theo giấy phép MIT.
