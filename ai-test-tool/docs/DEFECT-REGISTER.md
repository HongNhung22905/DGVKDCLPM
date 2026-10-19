# Bảng lỗi và trạng thái xử lý

Cập nhật tài liệu **20/10/2026**; bằng chứng thực thi thuộc **19/10/2026**. Lượt chính `04d381c9-e06b-453e-9601-2a698141b34a` có **85 ca: 75 PASS, 10 FAIL, 0 ERROR/SKIP**. Bốn nhóm HSK dưới đây quy về 10 ca thất bại, không phải 10 nguyên nhân gốc độc lập. [Truy vết từng ca](TEST-TRACEABILITY.md), [XML gốc](../experiments/2026-10-19/selenium-all-122951/report.xml).

Mức nghiêm trọng đề xuất: **S1** — ngừng hệ thống, mất dữ liệu quan trọng hoặc xâm phạm bảo mật đã xác nhận; **S2** — chặn luồng chính trong điều kiện kiểm thử; **S3** — sai kiểm tra đầu vào, hiển thị hoặc đồng bộ cục bộ nhưng còn sử dụng được phần khác; **S4** — trình bày nhỏ. Ưu tiên **P1** là xử lý/xác minh sớm, **P2** là xử lý kế tiếp. Mức độ và ưu tiên được phân loại khi lập báo cáo, chưa do chủ sản phẩm phê duyệt; không có phát hiện nào được xác nhận S1. Đây không phải bằng chứng hệ thống không có lỗi S1.

## Danh mục

| Mã | Ca liên quan / số FAIL lượt chính | Nghiêm trọng / ưu tiên đề xuất | Ảnh hưởng | Trạng thái |
| --- | --- | --- | --- | --- |
| HSK-001 | REG-09: `test_register_whitespace_name` / 1 | S3 / P2 | Lưu tài khoản có tên rỗng sau trim, không đáp ứng kiểm tra đầu vào | Mở — nguyên nhân có căn cứ; chưa sửa/chạy lại sau sửa |
| HSK-002 | VOC-01-HSK-1…7: `test_select_level_and_return[HSK-1…7]` / 7 | S2 trong luồng tự động hóa / P1 xác minh | Chặn thao tác quay về trong cả 7 ca; ảnh hưởng thao tác người dùng chưa được xác minh độc lập | Mở — đã xác nhận click bị che, cần tách lỗi bố cục và thời điểm Selenium |
| HSK-003 | STATS-03: `test_stats_calendar_and_ranges` / 1 | S3 / P1 | Có phiên học hôm nay nhưng lịch không hiển thị hoạt động ngày đó | Mở — nguyên nhân cửa sổ ngày có căn cứ; chưa sửa |
| HSK-004 | NOTE-04: `test_notebook[NOTE-04]` / 1 | S3 / P2 | UI còn thẻ/bộ đếm sau khi API đã xóa, gây hiểu nhầm trạng thái sổ tay | Mở — chưa ổn định, chưa xác định nguyên nhân gốc |
| TOOL-001 | Launcher tìm dữ liệu học tập sai cwd / không thuộc 85 ca | S2 / đã xử lý trong đợt | Snapshot không đọc được `public/data`, chặn kiểm thử tra từ | Đã sửa và kiểm tra lại luồng nhóm nhỏ; giữ lượt bị dừng riêng |

**Tổng FAIL website: 1 + 7 + 1 + 1 = 10.** TOOL-001, HTTP 503 của Gemini và các lỗi fixture cố ý không được cộng vào FAIL website.

## Độ chắc chắn của nguyên nhân

| Mã | Quan sát có bằng chứng | Mức chắc chắn và phần chưa xác định |
| --- | --- | --- |
| HSK-001 | Tạo tài khoản với tên toàn khoảng trắng thành công; tên sau trim rỗng; source kiểm tra trước trim | **Có căn cứ về nguyên nhân trực tiếp** từ test, source và truy vấn chỉ đọc; chưa suy rộng thành lỗi bảo mật |
| HSK-002 | 7 trace có click bị thanh điều hướng chặn sau cuộn | **Chắc về cơ chế thất bại của click**, chưa tách ảnh hưởng bố cục với thời điểm Selenium và chưa xác nhận phạm vi ảnh hưởng thao tác tay |
| HSK-003 | Lịch bỏ hôm nay; chạy đúng hàm với ngày 19/10/2026 cho lưới kết thúc 17/10 | **Có căn cứ về lỗi cửa sổ ngày tại thời điểm kiểm thử**; chưa kiểm tra đủ ngày trong tuần/biên tháng/năm |
| HSK-004 | API rỗng nhưng UI còn thẻ; PASS → FAIL → PASS giữa các lượt | **Chắc về sai khác quan sát**, nguyên nhân gốc **chưa xác định**; race do GET cũ ghi đè state chỉ là giả thuyết |
| TOOL-001 | Cwd tìm dữ liệu sai; sau đổi cwd luồng nhóm nhỏ đạt | **Có căn cứ và đã kiểm tra lại luồng**; chưa có unit test riêng cho hồi quy cwd |

Các mức trên không phải xác suất thống kê. Việc cần làm là mô tả và đánh giá tác động dựa trên bằng chứng; không bắt buộc sửa website để mọi ca PASS. Mốc nguồn và từng lượt được chốt trong [bảng minh chứng](EVIDENCE-BASELINE.md).

## Tiền điều kiện tái hiện chung

Chỉ sử dụng môi trường HSK kiểm thử riêng theo [hướng dẫn Neon](NEON-TEST-SETUP.md), chạy snapshot bằng `npm --prefix ai-test-tool run hsk:test`, rồi công cụ bằng `npm --prefix ai-test-tool start`. Không chạy test tạo/xóa dữ liệu trên database website đang sử dụng. Dùng test gốc, Chrome và nhóm tương ứng trong công cụ; log môi trường tại [selenium-environment.json](../experiments/2026-10-19/selenium-environment.json). Mô tả dưới đây là cách tái hiện dựa trên lượt cũ; cập nhật tài liệu không tạo thêm lượt chạy mới.

## HSK-001 — Tên chỉ có khoảng trắng

1. Trong môi trường riêng, mở `/register` với email kiểm thử mới và mật khẩu hợp lệ.
2. Nhập tên chỉ gồm khoảng trắng, gửi biểu mẫu; ca gốc: [test_register.py](../../selenium-tests/test_register.py), `test_register_whitespace_name`.
3. Đối chiếu phản hồi, giao diện và giá trị tên được lưu trên database kiểm thử.

**Mong đợi:** từ chối tên rỗng sau chuẩn hóa, không tạo tài khoản đó. **Thực tế:** tạo thành công; truy vấn chỉ đọc thấy một bản ghi tên rỗng. Source kiểm tra truthiness trước trim, chưa kiểm tra lại sau trim. Chưa xác nhận mất dữ liệu hay ảnh hưởng bảo mật.

Minh chứng: [ảnh REG-09](../experiments/2026-10-19/selenium-all-122951/REG-09-fail.png), [quan sát database kiểm thử](../experiments/2026-10-19/registration-whitespace-observation.json). Điều kiện đóng: kiểm tra tên sau chuẩn hóa, REG-09 đạt ở lượt mới và hồi quy đăng ký hợp lệ/đầu vào không hợp lệ không đổi sai.

## HSK-002 — Nút quay về bị che

1. Mở `/vocabulary`, chọn lần lượt cấp HSK 1…7 bằng luồng ca gốc [test_vocabulary.py](../../selenium-tests/test_vocabulary.py).
2. Sau khi các liên kết bài học hiển thị và trang tự cuộn, click nút “Chọn cấp độ” như `test_select_level_and_return`.
3. Ghi vị trí nút/thanh điều hướng, thời điểm cuộn và thao tác click; so sánh thêm với thao tác người dùng ở cùng viewport.

**Mong đợi:** click được và trở về danh sách cấp. **Thực tế:** 7 ca có `ElementClickInterceptedException`, tâm click `(234, 10)` bị thanh điều hướng nhận thay. Chưa đủ kết luận logic chọn cấp sai hoặc mọi người dùng đều bị chặn; việc tự cuộn mượt là yếu tố cần xác minh.

Minh chứng: [ảnh HSK 1](../experiments/2026-10-19/selenium-all-122951/VOC-01-HSK-1-fail.png), [traceback cả 7 ca](../experiments/2026-10-19/selenium-all-122951/RESULTS.md). Điều kiện đóng: xác minh nguồn lỗi UI/thời điểm kiểm thử, ghi giải pháp đúng phạm vi; 7 ca click theo tương tác người dùng đạt và có lượt kiểm tra lại. Không dùng click cưỡng bức hoặc đổi assertion chỉ để PASS.

## HSK-003 — Lịch không chứa ngày hiện tại

1. Dùng tài khoản kiểm thử mới, tạo phiên học hôm nay có 20 từ theo [test_stats_calendar.py](../../selenium-tests/test_stats_calendar.py), `test_stats_calendar_and_ranges`.
2. Xác nhận API và dòng lịch sử có phiên học; mở `/stats`, lần lượt chọn 4 tháng, 6 tháng và 1 năm.
3. Kiểm tra ô hoạt động của hôm nay; để đối chiếu lại bằng hàm, dùng dữ liệu ngày **19/10/2026** như minh chứng đã lưu. Script hiện tại dùng ngày chạy nên không bảo đảm tái hiện cùng biên ngày nếu chạy ngày khác.

**Mong đợi:** lưới chứa hôm nay và phản ánh phiên học. **Thực tế:** cả ba khoảng không có ô hoạt động; chạy đúng hàm `buildCalendarGrid` với dữ liệu ngày kiểm thử cho thấy lưới kết thúc **17/10/2026**. Không kết luận phiên học bị mất vì API/lịch sử vẫn có dữ liệu.

Minh chứng: [ảnh STATS-03](../experiments/2026-10-19/selenium-all-122951/STATS-03-fail.png), [đối chiếu hàm](../experiments/2026-10-19/calendar-function-observation.json). Điều kiện đóng: lưới bao gồm ngày hiện tại, STATS-03 đạt ở lượt mới và có kiểm tra ngày trong tuần/biên tháng/năm.

## HSK-004 — Xóa sổ tay nhưng UI chưa rỗng

1. Tạo tài khoản kiểm thử riêng và thêm từ vào sổ tay theo fixture của [test_notebook.py](../../selenium-tests/test_notebook.py).
2. Chạy NOTE-04 trong nhóm nhỏ và toàn bộ theo cùng trình tự đợt cũ; xóa từ, chờ DELETE và đọc lại API.
3. Ghi thứ tự GET/DELETE, phản hồi và cập nhật state; kiểm tra UI hiển thị “Sổ tay trống”.

**Mong đợi:** API rỗng và UI rỗng thống nhất. **Thực tế ở lượt đầy đủ:** API `entries == []`, UI còn một thẻ/bộ đếm 1 và timeout sau 30 giây. Chuỗi quan sát là **PASS nhóm nhỏ UI → FAIL lượt đầy đủ → PASS nhóm nhỏ CLI**; chưa có tỷ lệ tái hiện ổn định. Phản hồi GET cũ ghi đè state chỉ là giả thuyết, chưa được chứng minh.

Minh chứng: [ảnh NOTE-04](../experiments/2026-10-19/selenium-all-122951/NOTE-04-fail.png), [so sánh nhóm nhỏ](../experiments/2026-10-19/selenium-cli-ui-comparison.json). Điều kiện đóng: xác minh nguyên nhân, lưu giải pháp và log kiểm tra lại qua các lượt nhóm nhỏ/toàn bộ lặp có kiểm soát dữ liệu; một lượt PASS riêng lẻ chưa đủ đóng lỗi.

## TOOL-001 — Cwd của snapshot

Tái hiện lịch sử: launcher trước sửa chạy snapshot nhưng giữ cwd ở repo, luồng tìm kiếm không đọc được `public/data`. Đã đổi cwd vào snapshot trước `app.prepare()` trong [hsk-test-server.ts](../src/hsk-test-server.ts). [Lượt đầu bị dừng](../experiments/2026-10-19/selenium-notebook-122432/summary.json) không có XML đầy đủ; [lượt UI sau sửa](../experiments/2026-10-19/selenium-notebook-122623/summary.json) có 10/10 PASS. Đây là kiểm tra lại luồng, chưa có unit test riêng cho hồi quy cwd. Không chạy lại mã lỗi cũ hoặc thay lịch sử thành PASS.

Trạng thái “đã sửa và kiểm tra lại” chỉ áp dụng TOOL-001. Bốn phát hiện HSK chưa có mã sửa/lượt xác nhận sau sửa; xem [phân tích chi tiết](SELENIUM-RESULTS.md) và [kết luận chất lượng](EXPERIMENT-REPORT.md#8-kết-luận-chất-lượng-theo-tiêu-chí-và-phạm-vi-chưa-kiểm-thử).
