# Thực nghiệm công cụ HSK Test Lab

Kết quả ngày 19/10/2026 lưu trong [2026-10-19/](2026-10-19/). Báo cáo diễn giải ở [EXPERIMENT-REPORT.md](../docs/EXPERIMENT-REPORT.md).

Các script chạy từ thư mục gốc repository, giữ nguyên `.env.local` HSK. API key đọc từ `.env` bị Git bỏ qua; không đưa key vào lệnh hoặc kết quả. Các script gọi Gemini là yêu cầu thật có thể sử dụng hạn mức tài khoản; chỉ chạy lại khi cần thực nghiệm mới.

| Script | Mục đích | Lệnh |
| --- | --- | --- |
| `freeze-evidence.py` | Chốt/đối chiếu danh mục, hash minh chứng và kiểm kê JMeter lịch sử, không chạy test hay gọi DB/API | `python ai-test-tool/experiments/freeze-evidence.py --check` (bỏ `--check` để chốt lại) |
| `build-traceability.py` | Đối chiếu/sinh ma trận từ XML, test và log đã lưu; không chạy website hoặc gọi API/DB | `python ai-test-tool/experiments/build-traceability.py --check` (bỏ `--check` để sinh lại) |
| `check-gemini.ts` | Phân tích lỗi FC-05 lịch sử bằng key hiện tại | `node --env-file=ai-test-tool/.env ai-test-tool/experiments/check-gemini.ts` |
| `check-faults.ts` | XML hỏng, hủy, timeout và kết nối bị từ chối | `node ai-test-tool/experiments/check-faults.ts` |
| `compare-cli-ui.py` | Cùng bộ Vitest, chạy lệnh rồi chạy UI, đối chiếu XML bằng parser độc lập | `ai-test-tool/.venv/Scripts/python.exe ai-test-tool/experiments/compare-cli-ui.py` |
| `check-ui-guard.py` | Khi chưa có môi trường HSK kiểm thử: UI từ chối Selenium và XML hỏng | `ai-test-tool/.venv/Scripts/python.exe ai-test-tool/experiments/check-ui-guard.py` |
| `check-xml-compatibility.py` | Đối chiếu từng ca trong XML gốc với Python ElementTree | `ai-test-tool/.venv/Scripts/python.exe ai-test-tool/experiments/check-xml-compatibility.py` |
| `evaluate-ai.ts` | Tạo 10 lỗi có nguyên nhân đối chiếu, sau đó gọi Gemini với log lỗi | `node --env-file=ai-test-tool/.env ai-test-tool/experiments/evaluate-ai.ts` |
| `prepare-auth-fixture.ts` | Tạo tài khoản tiền điều kiện cho register/login/logout trên HSK test, không sửa tài khoản đã có | `node ai-test-tool/experiments/prepare-auth-fixture.ts` |
| `run-selenium-ui.py` | Chạy nhóm 10 ca hoặc 85 ca qua UI, lưu XML/log/ảnh và đối chiếu parser độc lập | `ai-test-tool/.venv/Scripts/python.exe ai-test-tool/experiments/run-selenium-ui.py --group selenium-notebook` (hoặc `selenium-all`) |
| `compare-selenium-cli.ts` | Chạy nhóm 10 ca bằng lệnh, đối chiếu lượt UI đã lưu; cần đợi UI xong | `node ai-test-tool/experiments/compare-selenium-cli.ts` |
| `summarize-selenium.ts` | Xuất bảng từng module và chi tiết lỗi từ lượt Selenium đầy đủ đã kết thúc | `node ai-test-tool/experiments/summarize-selenium.ts RUN_ID` |
| `verify-selenium-ui.py` | Mở lại từ lịch sử, đối chiếu từng ca DOM với XML gốc, không chạy lại test | `ai-test-tool/.venv/Scripts/python.exe ai-test-tool/experiments/verify-selenium-ui.py RUN_ID` |
| `diagnose-calendar.ts` | Trích đúng hàm lịch hiện có bằng AST, chạy độc lập với bản ghi hôm nay, không sửa source/DB | `node ai-test-tool/experiments/diagnose-calendar.ts` |

Các script UI yêu cầu công cụ đã mở ở cổng 4317. Chúng dùng Chrome headless, không tự mở HSK và không gọi database website hiện tại. `check-ui-guard.py` chỉ được dùng khi chưa mở HSK kiểm thử; không dùng làm script chạy Selenium thật.

Kết quả chấm AI là nhận xét sơ bộ của trợ lý Codex, không phải đánh giá độc lập bởi người dùng hoặc hội đồng. Ground truth lưu trước lời gọi AI, không được đưa vào prompt. Một mẫu dùng báo cáo HSK lịch sử; chín mẫu là lỗi có kiểm soát. Mỗi lỗi được gọi một lượt; riêng AI-08 có lưu lần HTTP 503 và lần thử lại. Không suy luận độ ổn định hoặc tỷ lệ chính xác chung của Gemini từ tập nhỏ này.

Bổ sung tài liệu ngày 20/10/2026: [truy vết từng ca](../docs/TEST-TRACEABILITY.md), [bảng lỗi](../docs/DEFECT-REGISTER.md), [phiếu độc lập chưa có điểm](../docs/AI-INDEPENDENT-REVIEW.md). Không sửa XML, câu trả lời AI hoặc điểm sơ bộ để khớp kết luận; số liệu thực nghiệm giữ mốc 19/10/2026.

Đã cấu hình HSK snapshot dùng endpoint Neon kiểm thử riêng theo [NEON-TEST-SETUP.md](../docs/NEON-TEST-SETUP.md). Nhóm nhỏ UI: [10/10 PASS](2026-10-19/selenium-notebook-122623/summary.json). Lượt đầy đủ: [75 PASS/10 FAIL trên 85 ca](2026-10-19/selenium-all-122951/summary.json). [Đối chiếu nhóm nhỏ CLI/UI](2026-10-19/selenium-cli-ui-comparison.json) cùng 10/10 PASS; NOTE-04 thất bại trong lượt đầy đủ vẫn được giữ nguyên. [85/85 ca DOM khớp XML](2026-10-19/selenium-dom-verification.json). Lượt bị dừng do launcher tìm sai thư mục dữ liệu được giữ ở `selenium-notebook-122432`, không cộng vào mẫu số 85. Xem [báo cáo Selenium](../docs/SELENIUM-RESULTS.md) để biết phân loại lỗi và giới hạn.
