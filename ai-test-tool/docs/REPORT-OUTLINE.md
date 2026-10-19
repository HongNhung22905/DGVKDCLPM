# Định hướng báo cáo chính thức

**Đề tài đã chốt:** “Kiểm thử tự động website hỗ trợ học tiếng Trung và xây dựng công cụ tích hợp AI hỗ trợ phân tích kết quả.”

Website HSK là đối tượng đánh giá chính của môn học. HSK Test Lab là sản phẩm hỗ trợ do dự án phát triển để điều phối test, tổng hợp kết quả và tích hợp Gemini giải thích lỗi. Thành công của công cụ không có nghĩa website đạt mọi yêu cầu; website có FAIL vẫn là một kết quả đánh giá có giá trị khi đủ bằng chứng.

Tài liệu này chốt bố cục và nguồn để viết, **chưa phải toàn bộ bài báo cáo chính thức sáu chương**. Hồ sơ số liệu đã chốt trong [bảng minh chứng](EVIDENCE-BASELINE.md); yêu cầu–tiêu chí–test–kết quả nằm trong [ma trận](TEST-TRACEABILITY.md). Không tạo số liệu bổ sung bằng cách cộng các lượt chạy lại.

| Chương | Nội dung và câu hỏi cần trả lời | Nguồn đã có / phần còn thiếu |
| --- | --- | --- |
| **1. Giới thiệu** | Vì sao cần đánh giá website học tiếng Trung; mục tiêu đánh giá HSK; phạm vi chức năng, giới hạn và hai sản phẩm: hồ sơ đánh giá, HSK Test Lab | Tên đề tài ở trên; phạm vi E-S02/E-V01; tách sản phẩm hỗ trợ khỏi đối tượng được đánh giá |
| **2. Cơ sở lý thuyết** | Trình bày kỹ thuật thực sự áp dụng: phân vùng tương đương, giá trị biên, chuyển trạng thái, hộp trắng và E2E; phân biệt số ca, bao phủ yêu cầu/code coverage, sample hiệu năng và lời giải thích AI | Dẫn ví dụ test xác thực, ngưỡng điểm 79/80/81 và luồng mở khóa/ôn tập có sẵn. Phần lý thuyết chính thức cần trích nguồn gốc phù hợp; chưa có phép đo code coverage để công bố |
| **3. Đặc tả và kế hoạch kiểm thử HSK** | Yêu cầu có mã và tiêu chí mong đợi; rủi ro và các ca; môi trường/phiên bản; điều kiện bắt đầu/kết thúc, cách xác định PASS/FAIL và giới hạn độ bao phủ | [Ma trận](TEST-TRACEABILITY.md), [mốc mã nguồn và môi trường](EVIDENCE-BASELINE.md), [Neon test](NEON-TEST-SETUP.md). Các tiêu chí rút từ test hiện có chưa thay thế đặc tả được chủ sản phẩm duyệt lại |
| **4. Thiết kế và xây dựng HSK Test Lab** | Kiến trúc local, nhóm test có sẵn, runner/hủy/timeout, đọc XML, lưu lịch sử và Gemini tùy chọn; cách ly môi trường website | [Thiết kế hiện có](EXPERIMENT-REPORT.md), source `src/` và `public/`. AI không sinh test hoặc tự phán assertion đúng/sai |
| **5. Thực hiện và phân tích kết quả** | Đánh giá HSK trước: 85 Selenium, 22 Vitest, kiểm tra API nằm trong E2E, phân tích 10 FAIL thành 4 nhóm. Sau đó đánh giá công cụ và AI; JMeter trình bày tách riêng theo mức bằng chứng | E-S02/E-V01, [bảng lỗi](DEFECT-REGISTER.md), E-T01/E-X01/E-F01 và E-A01…03. H-J01…10 là kết quả JMeter lịch sử chưa chốt đủ môi trường/ngưỡng; không tạo “bộ API độc lập” hoặc coi kết nối HTTP 200 là kiểm thử toàn bộ API |
| **6. Kết luận** | HSK đáp ứng/chưa đáp ứng gì trong phạm vi chạy; công cụ hỗ trợ được gì; giới hạn về phiên bản, coverage, môi trường, độ ổn định và AI; hướng phát triển | [Kết luận theo tiêu chí](EXPERIMENT-REPORT.md#8-kết-luận-chất-lượng-theo-tiêu-chí-và-phạm-vi-chưa-kiểm-thử). Chưa nghiệm thu toàn website, chưa xác nhận tiết kiệm thời gian con người hoặc độ chính xác AI tổng quát |

## Thứ tự hoàn thiện

1. **Chốt hồ sơ:** dùng ID E-* và H-J*; ghi HEAD được ghi nhận, working tree/hash và commit lưu trữ sau thực nghiệm đúng vai trò. Không gọi commit lưu sau khi chạy là clean commit đã được kiểm thử.
2. **Chốt ma trận:** mỗi yêu cầu có tiêu chí, test và kết quả; tham chiếu cùng XML và cùng run ID giữa các chương. 75/85 và NOTE-04 không ổn định được giữ nguyên.
3. **Dùng bảng lỗi:** giữ mức ảnh hưởng, cách tái hiện, độ chắc chắn và trạng thái. Không bắt buộc sửa website hoặc thay assertion để đạt toàn bộ.
4. **Viết bài chính thức theo sáu chương:** sử dụng bảng đã chốt, đánh số hình/bảng, dẫn nguồn lý thuyết, dẫn minh chứng thực nghiệm đúng lượt. Hồ sơ kỹ thuật hiện có là nguồn, không tự coi đã có đủ bài chính thức.
5. **Chỉ bổ sung thực nghiệm có mục đích:** ưu tiên [người chấm AI độc lập](AI-INDEPENDENT-REVIEW.md) và chẩn đoán NOTE-04/HSK-002. Lập lượt mới riêng, giữ mốc cũ; mọi thao tác tạo/xóa dữ liệu chỉ được dùng môi trường kiểm thử đã cách ly.

Không thêm chức năng công cụ, không viết lại bộ kiểm thử và không chạy JMeter/Selenium mới chỉ để đổi số liệu. Khi cần kiểm tra lại, nêu câu hỏi và tiền điều kiện dữ liệu trước, rồi bổ sung kết quả mới mà không ghi đè lịch sử.
