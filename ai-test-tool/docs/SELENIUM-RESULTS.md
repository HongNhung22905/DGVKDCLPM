# Kết quả kiểm thử Selenium — 19/10/2026

Ngày cập nhật tài liệu **20/10/2026**; giữ nguyên số liệu thực thi **19/10/2026**, không có lượt chạy mới trong lần biên tập này. [Ma trận truy vết từng ca](TEST-TRACEABILITY.md), [bảng lỗi, mức nghiêm trọng, cách tái hiện và trạng thái](DEFECT-REGISTER.md), [kết luận theo tiêu chí và phạm vi chưa kiểm thử](EXPERIMENT-REPORT.md#8-kết-luận-chất-lượng-theo-tiêu-chí-và-phạm-vi-chưa-kiểm-thử).

**Lượt đầy đủ: 85 ca, 75 PASS, 10 FAIL, 0 ERROR, 0 SKIP.** Tỷ lệ đạt 75/85 ≈ 88,24%; chưa kết luận website đạt toàn bộ phạm vi kiểm thử. Các lượt kiểm thử dùng endpoint Neon riêng, không ghi/xóa database website hiện tại.

## Môi trường và các lượt chạy

HSK được chạy từ snapshot riêng, dùng cấu hình `ai-test-tool/.env.hsk-test` với nhãn branch `hsk-test-2026-10-19`. Endpoint được kiểm tra khác endpoint website hiện tại. Trước khi chạy, giao dịch chỉ đọc xác nhận 12 bảng và 0 tài khoản; các lượt sau tự tạo dữ liệu kiểm thử. Nhãn branch lấy từ cấu hình người dùng; không truy cập Neon management API để xác minh tên branch từ phía Neon.

Lệnh khởi động: `npm --prefix ai-test-tool run hsk:test`. Các test website dùng Chrome có cửa sổ như mã gốc; trình duyệt điều khiển giao diện công cụ dùng Chrome headless. XML ghi nhận Chrome 154.0.8037.100. Các tệp Selenium và assertion giữ nguyên. Mã/hash môi trường ở [selenium-environment.json](../experiments/2026-10-19/selenium-environment.json) và [selenium-full-results.json](../experiments/2026-10-19/selenium-full-results.json).

| Lượt | Kết quả | Thời gian runner | Ý nghĩa |
| --- | --- | ---: | --- |
| Nhóm nhỏ qua UI | 10/10 PASS | 180,279 s | Chọn test → pytest → đọc XML → lưu lịch sử hoạt động |
| Toàn bộ qua UI | 75 PASS / 10 FAIL trên 85 ca | 1727,746 s (28 phút 47,746 giây) | Kết quả chính của đợt đầy đủ |
| Lượt đầu trước khi sửa launcher | Đã dừng; chưa có XML đầy đủ | 56,076 s | Không cộng vào kết quả nhóm nhỏ hoặc 85 ca |

Lượt đầu phát hiện launcher tìm `public/data` theo cwd của repo; đã sửa **công cụ** để đổi cwd vào snapshot trước `app.prepare()`. Lượt bị dừng được giữ [riêng](../experiments/2026-10-19/selenium-notebook-122432/summary.json), không sửa lịch sử thành PASS. Sau khi sửa, API tìm kiếm phản hồi HTTP 200 và nhóm nhỏ đạt 10/10.

Các ca cũ đăng nhập/đăng xuất/đăng ký email trùng cần tài khoản cố định. Dữ liệu tiền điều kiện đã được tạo bằng API đăng ký trên branch kiểm thử; không sửa test hoặc tài khoản đã tồn tại. Xem [auth-fixture.json](../experiments/2026-10-19/auth-fixture.json).

## Kết quả theo nhóm trong lượt 85 ca

| Nhóm | Tổng | PASS | FAIL |
| --- | ---: | ---: | ---: |
| Đăng ký, đăng nhập, đăng xuất | 18 | 17 | 1 |
| Từ vựng, flashcard | 17 | 10 | 7 |
| Mở khóa bài | 9 | 9 | 0 |
| Ôn tập SM-2 | 8 | 8 | 0 |
| Tiến độ, thống kê, cách ly dữ liệu | 8 | 7 | 1 |
| Luyện viết | 7 | 7 | 0 |
| Trò chơi | 8 | 8 | 0 |
| Tra từ, sổ tay | 10 | 9 | 1 |
| **Tổng** | **85** | **75** | **10** |

[Bảng từng file và traceback đầy đủ](../experiments/2026-10-19/selenium-all-122951/RESULTS.md), [XML gốc](../experiments/2026-10-19/selenium-all-122951/report.xml), [nhật ký](../experiments/2026-10-19/selenium-all-122951/output.log), [ảnh kết quả UI](../experiments/2026-10-19/selenium-all-122951/ui-result.png).

## Đối chiếu công cụ

Python ElementTree đối chiếu từng tên/classname/trạng thái với API: **85/85 khớp**. Mở lại lượt đầy đủ từ lịch sử trong trình duyệt và đối chiếu từng tên/trạng thái trên DOM với XML: **85/85 khớp**. Đây là bằng chứng công cụ tổng hợp đúng cả khi website có ca FAIL; không biến kết quả website thành PASS.

[Tóm tắt lượt đầy đủ](../experiments/2026-10-19/selenium-all-122951/summary.json), [đối chiếu DOM/XML](../experiments/2026-10-19/selenium-dom-verification.json), [ảnh mở lại từ lịch sử](../experiments/2026-10-19/selenium-history-result.png). Hash `.env.local` HSK trước/sau giống nhau.

## Các ca thất bại và mức kết luận

Mã lỗi thống nhất giữa các tài liệu: **HSK-001 = REG-09 (1 ca), HSK-002 = VOC-01-HSK-1…7 (7 ca), HSK-003 = STATS-03 (1 ca), HSK-004 = NOTE-04 (1 ca)**. Cả bốn đang mở, chưa có bản sửa và lượt kiểm tra lại sau sửa. Lỗi launcher TOOL-001 đã sửa thuộc lượt bị dừng riêng, không cộng vào 10 FAIL này. Mức nghiêm trọng đề xuất xem bảng lỗi; việc nhóm nhỏ chạy lại PASS không tự đóng HSK-004.

### REG-09: tên chỉ có khoảng trắng vẫn được chấp nhận

`test_register_whitespace_name` kỳ vọng từ chối, thực tế nhận trạng thái accepted. [Ảnh](../experiments/2026-10-19/selenium-all-122951/REG-09-fail.png) hiển thị “Tạo tài khoản thành công”. [Truy vấn chỉ đọc](../experiments/2026-10-19/registration-whitespace-observation.json) trên branch kiểm thử xác nhận có 1 bản ghi tên rỗng.

Rà soát `app/api/auth/register/route.ts` thấy kiểm tra truthiness của `name` trước khi trim, sau đó lưu `name.trim()` mà không kiểm tra rỗng lần nữa. Đây là nguyên nhân có căn cứ từ mã và trạng thái đã lưu; hành vi không đáp ứng kỳ vọng của REG-09. Chưa sửa website trong đợt này.

### VOC-01-HSK-1…7: click nút quay lại bị chặn

Cả 7 trường hợp đã chọn cấp và kiểm tra các liên kết bài học trước khi dừng tại thao tác quay về “Chọn cấp độ”. Traceback ghi `ElementClickInterceptedException`: tâm click `(234, 10)` bị phần tử thanh điều hướng nhận thay. [Ảnh HSK 1](../experiments/2026-10-19/selenium-all-122951/VOC-01-HSK-1-fail.png).

Mã VocabularyClient tự cuộn mượt tới phần bài sau khi chọn cấp. Cần kiểm tra vị trí nút, thanh điều hướng cố định và thời điểm cuộn trước khi click; sau đó đối chiếu thao tác bằng tay và Selenium. Kết quả hiện tại là lỗi tương tác UI/tự động hóa, **không đủ để kết luận logic chọn cấp HSK sai**. Không dùng JavaScript click hoặc đổi assertion để biến lượt này thành PASS.

### STATS-03: lịch bỏ sót ngày có phiên học hôm nay

`test_stats_calendar_and_ranges` xác nhận API và dòng lịch sử có phiên hôm nay 20 từ, nhưng cả các khoảng 4 tháng, 6 tháng, 1 năm đều không có ô hoạt động. [Ảnh](../experiments/2026-10-19/selenium-all-122951/STATS-03-fail.png).

Đã trích đúng hàm `buildCalendarGrid` từ source bằng TypeScript AST, transpile và chạy trong VM với một bản ghi ngày 19/10/2026. Cả ba khoảng đều kết thúc ở **17/10/2026**, không chứa hôm nay và trả 0 ô có dữ liệu. [Minh chứng](../experiments/2026-10-19/calendar-function-observation.json); script tái lập: `node ai-test-tool/experiments/diagnose-calendar.ts` (kết quả phụ thuộc ngày chạy). Không sửa source hoặc DB trong chẩn đoán này.

Nguyên nhân xác định được là cửa sổ ngày của lưới không bao gồm ngày hiện tại ở thời điểm kiểm thử. Cần sửa và kiểm tra các ngày trong tuần/biên tháng/năm trong đợt khắc phục riêng.

### NOTE-04: API đã xóa, UI vẫn giữ thẻ từ

Trong `test_notebook[NOTE-04]`, test đã chờ DELETE hoàn tất và API trả `entries == []`, sau đó timeout 30 giây khi đợi đoạn “Sổ tay trống”. [Ảnh cuối lỗi](../experiments/2026-10-19/selenium-all-122951/NOTE-04-fail.png) vẫn hiển thị một thẻ từ và bộ đếm 1.

Lượt nhóm nhỏ UI trước đó đạt ca này. Đây là dấu hiệu hành vi chưa ổn định; chưa xác định nguyên nhân gốc. Source có cả cập nhật state khi xóa và fetch danh sách khi thay đổi user; việc phản hồi cũ ghi đè state là giả thuyết cần log thứ tự request/state để xác minh, không phải kết luận đã chứng minh. Không quy lỗi cho DB xóa thất bại khi API đã xác nhận danh sách rỗng.

## Gemini trên lỗi của lượt thực tế

Đã gọi chức năng phân tích của công cụ với lỗi của lượt 85 ca: **HTTP 200**, phản hồi được lưu cùng lịch sử. [Toàn bộ phản hồi](../experiments/2026-10-19/selenium-gemini-analysis.json). Gemini nhóm được 10 lỗi thành bốn nhóm trên và gợi ý kiểm tra.

Phản hồi chỉ dựa trên XML/nhật ký rút gọn, không nhận ảnh hoặc mã nguồn đầy đủ. Nguyên nhân của REG-09 và STATS-03 ở báo cáo này dựa trên việc trợ lý kiểm tra source, dữ liệu kiểm thử và chạy hàm đối chiếu; đây không phải chấm AI độc lập bởi người đánh giá khác. Không mặc nhiên coi các giả thuyết của Gemini là sự thật. Một số đường dẫn API hoặc giả thuyết trong lời AI cần đối chiếu lại source. Phần này tách khỏi tập chấm AI 10 mẫu có kiểm soát trước đó.

## Thời gian và khả năng tái lập

XML lượt đầy đủ khai báo 1722,011 s; pytest console báo 1725,49 s; runner đo 1727,746 s. Các đồng hồ đo phạm vi khác nhau: thời gian báo cáo, toàn bộ tiến trình pytest và wrapper runner. Không gộp chúng thành một đại lượng.

Lượt nhóm nhỏ UI có 10/10 PASS, nhưng cùng nhóm nằm trong lượt đầy đủ có 9 PASS/1 FAIL do NOTE-04. Điều này cần được giữ trong báo cáo ngay cả khi lượt CLI tiếp theo đạt. Không thay kết quả chính bằng kết quả chạy lại.

Chưa đo thời gian thao tác/tổng hợp của người dùng thật; không kết luận giao diện làm Selenium chạy nhanh hơn. Chưa chạy lại toàn bộ sau sửa lỗi vì chưa sửa website hoặc các assertion.

### Nhóm nhỏ bằng CLI so với UI

Lượt CLI sau lượt đầy đủ cũng đạt **10/10 PASS**, exit code 0. Tên/classname/trạng thái từng ca giống lượt UI nhóm nhỏ. XML CLI: 153,517 s; toàn bộ tiến trình CLI: 155,019 s. UI nhóm nhỏ: XML 178,580 s, runner 180,279 s. [Bảng đối chiếu](../experiments/2026-10-19/selenium-cli-ui-comparison.json), [XML CLI](../experiments/2026-10-19/selenium-notebook-cli-2026-10-19T12-58-44-003Z/report.xml), [log CLI](../experiments/2026-10-19/selenium-notebook-cli-2026-10-19T12-58-44-003Z/output.log).

NOTE-04 có chuỗi quan sát **PASS ở UI nhóm nhỏ → FAIL trong lượt đầy đủ → PASS ở CLI nhóm nhỏ**. Điều này cho thấy cần kiểm tra tính ổn định và đồng bộ state, chưa đủ xác định nguyên nhân gốc. Lượt CLI không làm lượt đầy đủ thành 76 PASS.
