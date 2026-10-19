# Chốt kết quả và danh mục minh chứng

Đề tài: **Kiểm thử tự động website hỗ trợ học tiếng Trung và xây dựng công cụ tích hợp AI hỗ trợ phân tích kết quả.** Đánh giá website HSK là trọng tâm môn học; HSK Test Lab là sản phẩm hỗ trợ được phát triển trong dự án.

Chốt hồ sơ ngày **20/10/2026** từ các tệp đã có; không chạy thêm test hoặc truy cập DB. Số liệu đợt chính thuộc **19/10/2026**. Các giờ dưới đây đã đổi sang UTC+7; JSON/XML giữ timestamp gốc. “Đối chiếu/ghi nhận” không có nghĩa là thời điểm bắt đầu chạy.

## 1. Phiên bản và môi trường

- HEAD được ghi trong `environment.json`: `197b22007f208b3fc9fd77ebfca3d22aecd18f0c`. Khi ghi metadata, công cụ và báo cáo còn ở working tree, chưa commit; không có một clean commit được xác nhận đại diện toàn bộ lần chạy.
- Commit lưu trữ mã/minh chứng sau thực nghiệm: `ce3290af09456590f2b98a9dcfcb51a7320f25b6`. Không gọi commit này là commit đã được chạy test vào thời điểm trước đó. Hash các tệp nguồn được ghi theo từng giai đoạn trong manifest bên dưới.
- Metadata trước Selenium và metadata sau sửa launcher khác hash `hsk-test-server.ts` đúng với thay đổi cwd đã ghi nhận. Hash của 33 tệp Selenium khớp hồ sơ lượt đầy đủ; các hash này không bao phủ toàn bộ mã website hoặc toàn bộ snapshot.
- Selenium: Windows, Python 3.14, pytest/Selenium theo bộ dependency đã khóa, Chrome 154.0.8037.100; HSK snapshot local, endpoint Neon khác website hiện tại. Nhãn cấu hình `hsk-test-2026-10-19` chưa được xác minh qua Neon management API. Không đưa URL DB/khóa API vào bảng.
- Vitest: Node 24.19.0, Vitest 2.1.9, không cần DB cho 22 ca hộp trắng. Test công cụ dùng fixture/mock và tiến trình riêng. UI/CLI Selenium cùng snapshot nhưng không reset DB giữa lượt, nên không coi dữ liệu hoàn toàn đồng nhất.

Nguồn: [metadata ban đầu](../experiments/2026-10-19/environment.json), [metadata Selenium](../experiments/2026-10-19/selenium-environment.json), [hash test của lượt đầy đủ](../experiments/2026-10-19/selenium-full-results.json), [dependency Python](../requirements-lock.txt), [manifest SHA-256](../experiments/2026-10-20/evidence-baseline.json).

## 2. Bảng tổng hợp được dùng trong báo cáo

| ID | Vai trò | Thời gian và loại mốc | Môi trường | Kết quả được dùng | Minh chứng / run ID |
| --- | --- | --- | --- | --- | --- |
| E-S02 | Kết quả chính — Selenium toàn bộ | 19/10/2026 19:29:55 UTC+7 (bắt đầu) | HSK snapshot local; Chrome 154; endpoint Neon kiểm thử riêng | 85: 75 PASS / 10 FAIL / 0 ERROR / 0 SKIP; runner 1727,746 s | [Tệp nguồn](../experiments/2026-10-19/selenium-all-122951/report.xml); `04d381c9-e06b-453e-9601-2a698141b34a` |
| E-V01 | Kết quả chính — logic HSK (Vitest) | 19/10/2026 19:04:17 UTC+7 (đối chiếu) | Windows, Node 24.19.0, Vitest 2.1.9; không cần DB | 22/22 PASS mỗi cách; không cộng CLI và UI thành 44 ca | [Tệp nguồn](../experiments/2026-10-19/cli-ui-comparison.json); `2d86db62-08ff-4356-bce3-cd18baca4d48` |
| E-S01 | Đối chiếu luồng — Selenium nhóm nhỏ UI | 19/10/2026 19:26:26 UTC+7 (bắt đầu) | Cùng môi trường snapshot/endpoint kiểm thử của E-S02 | 10/10 PASS, runner 180,279 s; không thay kết quả E-S02 | [Tệp nguồn](../experiments/2026-10-19/selenium-notebook-122623/report.xml); `f0662ff9-e0fa-4896-8ecd-71e492a1b081` |
| E-S03 | Đối chiếu — Selenium nhóm nhỏ CLI | 19/10/2026 20:01:19 UTC+7 (đối chiếu) | Cùng snapshot/endpoint; CLI chạy sau E-S02; không reset DB | 10/10 PASS; tiến trình 155,019 s; tên/trạng thái khớp E-S01 | [Tệp nguồn](../experiments/2026-10-19/selenium-cli-ui-comparison.json) |
| E-T01 | Sản phẩm hỗ trợ — test HSK Test Lab | 19/10/2026 (thư mục đợt; log không ghi giờ) | Node test runner; fixture/mock và tiến trình Node; không phải E2E HSK | 21/21 test công cụ đạt; không cộng vào 22 Vitest hoặc 85 Selenium | [Tệp nguồn](../experiments/2026-10-19/tool-tests-after-selenium.log) |
| E-X01 | Khả năng nhập — XML lịch sử | 19/10/2026 (thư mục đợt; JSON không ghi giờ) | Parser công cụ đối chiếu Python ElementTree trên cùng tệp | 70/70 XML khớp, 115 bản ghi có trùng; không phải 70 lượt chạy mới | [Tệp nguồn](../experiments/2026-10-19/xml-compatibility.json) |
| E-F01 | Tình huống lỗi công cụ | 19/10/2026 19:00:07 UTC+7 (ghi nhận) | XML và tiến trình/HTTP fixture local có kiểm soát | Hủy/timeout/XML sai/kết nối bị từ chối; không phải lỗi website mới | [Tệp nguồn](../experiments/2026-10-19/fault-scenarios.json) |
| E-A01 | Tích hợp — Gemini với lỗi HSK lịch sử | 19/10/2026 19:00:40 UTC+7 (ghi nhận) | Gemini API thật; alias gemini-flash-latest | HTTP 200; FC-05 lịch sử; không phải ca Selenium mới | [Tệp nguồn](../experiments/2026-10-19/gemini-connection.json); `33c87c5e-2069-4884-bf37-d79fe5b853b9` |
| E-A02 | AI — bộ 10 mẫu, đánh giá sơ bộ | 19/10/2026 19:07:25 UTC+7 (metadata; retry có timestamp riêng) | 1 lỗi HSK lịch sử + 9 lỗi kiểm soát; nguyên nhân lưu trước lời gọi | 7 đúng / 3 đúng một phần / 0 sai; chưa chấm độc lập; 503 lưu riêng | [Tệp nguồn](../experiments/2026-10-19/ai-judgements.json) |
| E-A03 | Tích hợp — Gemini với lỗi lượt đầy đủ | 19/10/2026 20:00:08 UTC+7 (ghi nhận) | Gemini nhận XML/log rút gọn của E-S02 | HTTP 200; không phải phần chấm 10 mẫu E-A02 | [Tệp nguồn](../experiments/2026-10-19/selenium-gemini-analysis.json); `04d381c9-e06b-453e-9601-2a698141b34a` |
| E-S00 | Loại khỏi kết quả chính — lượt bị dừng trước sửa launcher | 19/10/2026 19:24:37 UTC+7 (bắt đầu) | Snapshot trước sửa cwd; không đồng nhất phiên bản launcher E-S02 | cancelled; 56,076 s; chưa có XML đầy đủ; không cộng ca | [Tệp nguồn](../experiments/2026-10-19/selenium-notebook-122432/summary.json); `19e9e179-29de-494e-8580-e9c4591beffc` |

E-S02 là mẫu số chính của kết luận E2E: **85 ca, 75 PASS, 10 FAIL**. E-V01 là bộ logic 22 ca riêng. E-S01/E-S03 là chạy lại một tập con để đối chiếu luồng, không thêm ca độc lập vào tổng. E-T01 đánh giá công cụ, không thay kết quả website. E-X01 xác minh khả năng nhập báo cáo lịch sử, không xác nhận website hiện tại đạt các báo cáo đó.

## 3. Minh chứng JMeter lịch sử, chưa đưa vào kết luận đạt hiệu năng

Các JTL đã tồn tại trước đợt điều phối bằng HSK Test Lab, dù timestamp đều cùng ngày 19/10/2026. Phân loại lịch sử theo lượt/nguồn, không chỉ theo ngày. Chỉ kiểm kê số dòng sample và khoảng timestamp từ tệp; chưa chốt commit website, DB/môi trường, cấu hình tải, assertion, ngưỡng chấp nhận hoặc tính tương đương giữa các lượt. Tên `PROD`, `05`, `10`, `20` không đủ xác minh môi trường hay số người dùng thực tế.

| ID | JTL gốc | Khoảng sample UTC+7 | Số bản ghi sample (không phải testcase) | Báo cáo có sẵn |
| --- | --- | --- | ---: | --- |
| H-J01 | [PERF-01.jtl](../../PERF-01.jtl) | 19/10/2026 12:29:26 UTC+7 → 19/10/2026 12:31:26 UTC+7 | 756 | [HTML](../../PERF-01-report/index.html) |
| H-J02 | [PERF-PROD-05-R1.jtl](../../PERF-PROD-05-R1.jtl) | 19/10/2026 12:48:50 UTC+7 → 19/10/2026 12:50:49 UTC+7 | 819 | [HTML](../../PERF-PROD-05-R1-report/index.html) |
| H-J03 | [PERF-PROD-10-R1.jtl](../../PERF-PROD-10-R1.jtl) | 19/10/2026 12:53:45 UTC+7 → 19/10/2026 12:55:45 UTC+7 | 1434 | [HTML](../../PERF-PROD-10-R1-report/index.html) |
| H-J04 | [PERF-PROD-20-R2.jtl](../../PERF-PROD-20-R2.jtl) | 19/10/2026 13:00:24 UTC+7 → 19/10/2026 13:02:23 UTC+7 | 2105 | [HTML](../../PERF-PROD-20-R2-report/index.html) |
| H-J05 | [PERF-PROD-20-R3.jtl](../../PERF-PROD-20-R3.jtl) | 19/10/2026 13:04:29 UTC+7 → 19/10/2026 13:06:29 UTC+7 | 2110 | [HTML](../../PERF-PROD-20-R3-report/index.html) |
| H-J06 | [PERF-PROGRESS-05-R1.jtl](../../PERF-PROGRESS-05-R1.jtl) | 19/10/2026 13:31:35 UTC+7 → 19/10/2026 13:56:54 UTC+7 | 2819 | Chưa có |
| H-J07 | [PERF-PROGRESS-05-R2.jtl](../../PERF-PROGRESS-05-R2.jtl) | 19/10/2026 14:02:43 UTC+7 → 19/10/2026 14:04:43 UTC+7 | 996 | [HTML](../../PERF-PROGRESS-05-R2-report/index.html) |
| H-J08 | [PERF-PROGRESS-05-R3.jtl](../../PERF-PROGRESS-05-R3.jtl) | 19/10/2026 14:10:24 UTC+7 → 19/10/2026 14:12:24 UTC+7 | 1030 | [HTML](../../PERF-PROGRESS-05-R3-report/index.html) |
| H-J09 | [PERF-PROGRESS-10-R1.jtl](../../PERF-PROGRESS-10-R1.jtl) | 19/10/2026 14:15:23 UTC+7 → 19/10/2026 14:17:23 UTC+7 | 1563 | [HTML](../../PERF-PROGRESS-10-R1-report/index.html) |
| H-J10 | [PERF-PROGRESS-20-R1.jtl](../../PERF-PROGRESS-20-R1.jtl) | 19/10/2026 14:18:43 UTC+7 → 19/10/2026 14:20:43 UTC+7 | 2447 | [HTML](../../PERF-PROGRESS-20-R1-report/index.html) |

Kế hoạch hiện có: [HSK-performance.jmx](../../HSK-performance.jmx), [HSK-progress-performance.jmx](../../HSK-progress-performance.jmx). Chưa khẳng định từng lượt lịch sử chạy đúng phiên bản hiện tại của các JMX này. Không cộng sample JMeter với ca Selenium/Vitest, không suy mẫu thành PASS nghiệp vụ hoặc kết luận website đạt tải. Chương 5 có thể trình bày kiểm kê lịch sử với giới hạn trên; kết luận định lượng hiệu năng cần hồ sơ môi trường và ngưỡng được xác định trước lượt bổ sung.

## 4. Quy tắc viết và sử dụng minh chứng

1. Dùng ID E-* cho kết quả đợt chính/đối chiếu và H-J* cho JMeter lịch sử. Mỗi bảng số liệu của chương 3–6 phải chỉ rõ bộ nào; không gộp lại thành tổng ca mới.
2. Kiểm tra API trong Selenium (status/body/CRUD/persistence) thuộc chính ca Selenium đó. Chưa có bộ kiểm thử API độc lập được chốt trong hồ sơ này; HTTP 200 của Gemini là kết nối tích hợp, không phải PASS toàn bộ API HSK.
3. Giữ E-S00 cancelled và các FAIL gốc. Bốn nhóm HSK-001…004 quy về 10 FAIL; nhóm nhỏ PASS không đóng NOTE-04. Không cần sửa website để làm đẹp số liệu.
4. Đánh giá AI E-A02 là sơ bộ, chưa có người chấm độc lập; không công bố độ chính xác chung 70%. HTTP 503 lưu riêng với câu trả lời retry.
5. Hash manifest khóa nội dung tệp được dùng trong báo cáo, không thay thế việc biết commit/môi trường tại thời điểm chạy. Không bổ sung metadata hồi tố như thể đã thu thập trong quá trình thực thi.

Ma trận: [yêu cầu–tiêu chí–test–kết quả](TEST-TRACEABILITY.md). Lỗi: [mức ảnh hưởng, cách tái hiện và độ chắc chắn](DEFECT-REGISTER.md). Bố cục báo cáo: [sáu chương](REPORT-OUTLINE.md).

Kiểm tra hồ sơ bằng `python ai-test-tool/experiments/freeze-evidence.py --check`; bỏ `--check` chỉ khi chủ động chốt lại tệp đã thay đổi. Script không tạo lượt test mới, không dùng khóa API và không gọi database.
