# HSK Test Lab

Công cụ local độc lập để chọn và chạy **các bài kiểm thử có sẵn** của website HSK, đọc JUnit XML, hiển thị PASS/FAIL, lưu lịch sử và dùng Gemini giải thích lỗi. Công cụ không sinh test, không đánh giá tính đúng đắn của assertion và không sửa chức năng website HSK.

## Khởi động

Cần Node.js **22.18 trở lên** (đã kiểm tra với Node 24). Chạy từ thư mục gốc repository:

```powershell
npm --prefix ai-test-tool ci
npm --prefix ai-test-tool start
```

Mở **http://localhost:4317**. Không cần API key để chạy test, nhập XML hoặc xem lịch sử. Giao diện và backend chạy chung một server, chỉ lắng nghe trên `127.0.0.1`.

Để phát triển với tự khởi động lại backend: `npm --prefix ai-test-tool run dev`.

### Vitest

Công cụ gọi trực tiếp Vitest đã cài trong `hsk-app/frontend`, dùng cấu hình `vitest.config.mts` có sẵn. Nếu chưa cài dependency của HSK:

```powershell
npm --prefix hsk-app/frontend ci
```

Có ba lựa chọn: toàn bộ 22 ca, 17 ca SM-2/mở khóa, hoặc 5 ca ngưỡng điểm/bảo toàn kết quả. Không cần khởi động website hay database để chạy bộ hộp trắng này. XML mới được ghi vào thư mục dữ liệu của công cụ; không ghi đè `whitebox-results.xml` của HSK.

### Selenium

Cần Python 3.10 trở lên, Chrome và môi trường có pytest/Selenium. Có thể tạo môi trường riêng trong công cụ:

```powershell
python -m venv ai-test-tool/.venv
& ai-test-tool/.venv/Scripts/python.exe -m pip install -r ai-test-tool/requirements-lock.txt
```

Trên Linux/macOS, dùng `ai-test-tool/.venv/bin/python` thay đường dẫn `Scripts/python.exe`.

Công cụ ưu tiên Python trong `.venv`, sau đó dùng `python` trên PATH. Đặt `PYTHON_EXECUTABLE` trong `.env` nếu muốn dùng môi trường khác. Selenium Manager có thể cần Internet trong lần đầu tải ChromeDriver phù hợp.

Tạo Neon branch riêng và điền kết nối vào `.env.hsk-test` theo [hướng dẫn môi trường kiểm thử](docs/NEON-TEST-SETUP.md). Giữ nguyên `.env.local` của website hiện tại. Khởi động snapshot HSK kiểm thử trong terminal khác:

```powershell
npm --prefix ai-test-tool run hsk:test
```

Các test Selenium hiện có dùng cố định `http://localhost:3000`, mở Chrome có cửa sổ, và có thể tạo tài khoản/dữ liệu học tập. Launcher kiểm tra endpoint Neon khác endpoint hiện tại, chạy snapshot riêng và cung cấp marker môi trường. Runner từ chối chạy Selenium nếu marker không khớp. Chưa có URL của branch kiểm thử thì không khởi động HSK kiểm thử và không chạy Selenium có ghi dữ liệu.

Có các nhóm xác thực, từ vựng/flashcard, mở khóa, ôn tập, tiến độ/thống kê, luyện viết, trò chơi, tra từ/sổ tay và toàn bộ Selenium. Mỗi thời điểm chỉ chạy một nhóm. Ảnh chụp do test tạo được lưu trong thư mục của lần chạy tương ứng.

Để kiểm tra việc thu thập ca mà chưa chạy trình duyệt:

```powershell
& ai-test-tool/.venv/Scripts/python.exe -m pytest selenium-tests --collect-only -q
```

### Gemini (tùy chọn)

```powershell
Copy-Item ai-test-tool/.env.example ai-test-tool/.env
```

Sửa `ai-test-tool/.env`:

```dotenv
GEMINI_API_KEY=key_của_bạn
GEMINI_MODEL=gemini-flash-latest
```

Khởi động lại công cụ sau khi đổi biến môi trường. `GEMINI_MODEL` chỉ là tên model, có thể thay bằng model tài khoản đang hỗ trợ. Công cụ không đọc `.env.local` của website HSK, không trả API key về trình duyệt và không truyền Gemini key cho tiến trình test.

Sau một lần chạy có lỗi, mở **Phân tích AI** và bấm **Phân tích lỗi bằng Gemini**. Công cụ chỉ gửi dữ liệu khi bấm nút này: thông tin tổng hợp, tối đa 15 ca lỗi và phần cuối nhật ký đã rút gọn. Công cụ che một số dạng key, token, mật khẩu và email phổ biến; việc che tự động không bảo đảm nhận diện mọi dữ liệu nhạy cảm. Có thể xem nội dung lỗi/nhật ký trước khi gửi.

Gemini chỉ giải thích bằng chứng và đề xuất các bước kiểm tra. Giả thuyết AI cần được người dùng xác minh; không thay đổi trạng thái kiểm thử. Lỗi key, hạn mức, model hoặc mạng không làm mất kết quả chạy. Phân tích thành công được lưu lại cùng lần chạy và được sử dụng lại khi mở lịch sử.

Tích hợp sử dụng REST `generateContent`, theo [tài liệu Gemini chính thức](https://ai.google.dev/api/generate-content).

## Luồng sử dụng

1. Chọn Vitest/Selenium, nhóm test và giới hạn thời gian (10–7200 giây).
2. Bấm **Chạy kiểm thử**. Có thể mở **Nhật ký** trong lúc chạy hoặc bấm **Dừng test**.
3. Xem số ca đạt/thất bại/lỗi/bỏ qua, lọc ca và mở chi tiết thông báo lỗi.
4. Nếu cần, phân tích lỗi bằng Gemini.
5. Mở **Lịch sử chạy** để tìm lại kết quả; nút **XML** tải báo cáo gốc.

**Nhập XML** hỗ trợ JUnit XML từ Vitest và pytest, tối đa 8 MB/20.000 testcase. Báo cáo nhập được đánh dấu nguồn riêng; ngày hiển thị là ngày nhập và thời gian thực thi lấy từ XML. Không suy luận XML cũ là kết quả của phiên bản mã hiện tại.

| Trạng thái | Ý nghĩa |
| --- | --- |
| PASS | Có ca đạt, không có ca lỗi/thất bại, XML nhất quán và tiến trình thoát thành công nếu chạy trực tiếp |
| FAIL | XML ghi nhận ca có `failure` |
| LỖI | Lỗi thực thi/thu thập, testcase có `error`, thiếu XML, XML không đầy đủ hoặc tiến trình thất bại mà không có kết quả phù hợp |
| BỎ QUA | Tất cả các ca trong báo cáo đều bị bỏ qua; không tính là PASS |
| ĐÃ DỪNG / HẾT THỜI GIAN | Cây tiến trình test đã được yêu cầu dừng; XML nếu có chỉ là kết quả một phần |
| GIÁN ĐOẠN | Công cụ khởi động lại khi lịch sử còn lần chạy chưa kết thúc; không suy luận PASS/FAIL |

Tỷ lệ đạt = số ca PASS / tổng số testcase đọc được, bao gồm cả ca bỏ qua/lỗi trong mẫu số. Báo cáo không có testcase không được tính là đạt. Thời gian chạy trực tiếp tính cả khởi động tiến trình; thời gian nhập lấy từ XML.

## Dữ liệu và cấu trúc

```text
ai-test-tool/
  src/             Backend TypeScript, runner, đọc XML, Gemini, lưu lịch sử
  public/          Giao diện tiếng Việt (HTML/CSS/JavaScript)
  tests/           Kiểm tra parser, runner, API và Gemini với phản hồi giả lập
  data/runs/<id>/  run.json, report.xml, output.log và ảnh Selenium (nếu có)
  .env.example     Mẫu cấu hình, không chứa key thật
```

`data/`, `.env`, `.venv`, cache và `node_modules/` không được đưa vào Git. Lịch sử lưu trên đĩa, dùng ghi JSON qua tệp tạm rồi đổi tên, giữ sau khi khởi động lại. Lịch sử không tự xóa; cần sao lưu/dọn thư mục dữ liệu khi sử dụng lâu dài. Nhật ký chỉ giữ phần cuối tối đa khoảng 1 MB. XML và ảnh gốc được giữ local.

Backend chỉ cho thực thi các nhóm test cố định, không nhận lệnh shell/đường dẫn tùy ý từ trình duyệt. Dừng/hết thời gian dùng `taskkill /T /F` trên Windows hoặc dừng process group trên Unix. Khi đóng terminal bằng Ctrl+C, công cụ dừng tiến trình test đang quản lý. Nếu máy mất điện hoặc server bị buộc kết thúc, nên kiểm tra tiến trình trình duyệt còn sót trước khi chạy lại.

## Kiểm tra công cụ

```powershell
npm --prefix ai-test-tool run check
npm --prefix ai-test-tool test
```

Các test sử dụng tiến trình Node thật để kiểm tra FAIL, thiếu XML, hủy và timeout; Gemini dùng phản hồi giả lập, không gọi API trả phí. Bộ này kiểm tra công cụ, không thay thế các test của website HSK.

Kiểm tra giao diện bằng Chrome headless, khi công cụ đã chạy ở cổng 4317 và **chưa cấu hình Gemini key**:

```powershell
& ai-test-tool/.venv/Scripts/python.exe ai-test-tool/tests/browser_smoke.py
```

Kịch bản kiểm tra chọn nhóm, chạy 5 test Vitest thật, xem nhật ký, nhập XML hộp trắng có sẵn, lọc kết quả, lịch sử và bố cục mobile. Các báo cáo thật này được giữ trong lịch sử; ảnh giao diện nằm ở `data/qa/`.

Phạm vi hiện tại không gồm đánh giá assertion, sinh test bằng AI hoặc JMeter runner. Đã có [báo cáo thực nghiệm](docs/EXPERIMENT-REPORT.md) và [kết quả đầy đủ 85 ca Selenium](docs/SELENIUM-RESULTS.md), phân biệt kết quả công cụ, test website và báo cáo lịch sử. Các lượt Selenium dùng endpoint Neon kiểm thử riêng.

Cập nhật tài liệu 20/10/2026: [bảng chốt minh chứng và phiên bản](docs/EVIDENCE-BASELINE.md), [truy vết yêu cầu → tiêu chí → từng ca → kết quả](docs/TEST-TRACEABILITY.md), [bảng lỗi và trạng thái](docs/DEFECT-REGISTER.md), [phiếu chấm AI độc lập chưa thực hiện](docs/AI-INDEPENDENT-REVIEW.md). Đề tài đã chốt đặt đánh giá HSK làm trọng tâm, công cụ là sản phẩm hỗ trợ; [bố cục sáu chương](docs/REPORT-OUTLINE.md). Kết luận theo tiêu chí ở mục 8 báo cáo thực nghiệm; giữ nguyên số liệu ngày 19/10/2026. AI vẫn là đánh giá sơ bộ, chưa có độ chính xác tổng quát được xác nhận.

### Kết quả kiểm tra công cụ ngày 19/10/2026

- TypeScript và kiểm tra cú pháp JavaScript đạt.
- 21/21 kiểm thử công cụ đạt (mốc đầu tiên là 18/18, bổ sung 3 kiểm tra cách ly môi trường HSK), bao gồm tiến trình thật, hủy, timeout, lịch sử, API và Gemini giả lập.
- Bộ hộp trắng HSK chạy qua API công cụ: 22/22 PASS. Nhóm ngưỡng điểm chạy qua giao diện: 5/5 PASS.
- 7 nhóm thao tác Chrome headless đạt; kiểm tra thêm viewport mobile 390 px không tràn ngang.
- Đối chiếu thành công 70/70 tệp XML với Python ElementTree độc lập (115 bản ghi testcase lịch sử; không cộng thành kết quả đánh giá website).
- Selenium đã chạy đủ 85 ca trên HSK kiểm thử: 75 PASS/10 FAIL/0 ERROR/0 SKIP. Nhóm nhỏ UI và CLI đều 10/10 PASS, nhưng NOTE-04 thất bại trong lượt đầy đủ; giữ nguyên cả ba kết quả.
- Key Gemini mới đã gọi API thật thành công HTTP 200 trên lỗi FC-05 lịch sử. Đã lưu 10 phản hồi và nhận xét sơ bộ của trợ lý; chưa có đánh giá độc lập. Có một lần HTTP 503 được lưu và thử lại riêng.
- Cặp lượt Vitest bằng lệnh/UI đều 22/22 PASS; nhóm Selenium nhỏ bằng lệnh/UI đều 10/10 PASS. Từng ca và 85/85 ca mở lại từ lịch sử khớp XML gốc. Thời gian được tách rõ trong báo cáo, chưa đo thao tác người dùng.
- Gemini đã phân tích lỗi của lượt 85 ca thực tế thành công HTTP 200 và lưu trong lịch sử. Chưa sửa website hoặc assertion để thay đổi các kết quả FAIL.
