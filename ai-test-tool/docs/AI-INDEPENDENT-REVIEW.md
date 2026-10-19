# Phiếu chấm AI độc lập — chưa thực hiện

Ngày chuẩn bị **20/10/2026**. **Trạng thái: chưa có người chấm độc lập, chưa có điểm độc lập.** Phiếu này là kế hoạch và biểu mẫu trống, không phải kết quả thực nghiệm mới. Đánh giá hiện có vẫn mang nhãn **đánh giá sơ bộ bởi trợ lý Codex**: 7 đúng, 3 đúng một phần trên 10 mẫu, không phải “độ chính xác chung 70%”.

## Nguồn và cách chấm

- [Bộ mẫu gốc](../experiments/2026-10-19/ai-dataset.json): ID, log, nguyên nhân đã biết và bước kiểm tra mong đợi; lập trước khi gọi AI, không đưa nguyên nhân đối chiếu vào prompt.
- [Phản hồi nguyên bản](../experiments/2026-10-19/ai-responses.json): dùng câu trả lời thành công của từng ID; giữ lỗi dịch vụ và lịch sử retry riêng.
- [Điểm sơ bộ hiện có](../experiments/2026-10-19/ai-judgements.json): chỉ mở để so sánh sau khi người chấm đã nộp điểm độc lập. Không dùng điểm sơ bộ làm đáp án chấm.

Người chấm cần có khả năng đọc log kiểm thử và không tham gia tạo phản hồi hoặc chấm sơ bộ. Ghi tên/mã người chấm, vai trò, quan hệ với dự án, ngày chấm và phiên bản bộ mẫu/phản hồi (commit hoặc hash). Có thể bắt đầu với một người; khi có hai người, mỗi người nộp phiếu riêng trước khi thảo luận bất đồng. Một trợ lý tự chấm lại không được ghi là người đánh giá độc lập.

Mỗi mẫu: đọc log và phản hồi, đối chiếu nguyên nhân đã biết, ghi bằng chứng cho điểm ở **hai trục riêng**:

| Trục | 0 điểm | 1 điểm | 2 điểm |
| --- | --- | --- | --- |
| Nguyên nhân | Trái bằng chứng | Nhận diện nhóm lỗi nhưng thiếu nguyên nhân trực tiếp | Nêu đúng nguyên nhân trực tiếp đã biết |
| Bước kiểm tra/xử lý | Sai hoặc làm mất mục tiêu kiểm thử | Có bước hữu ích nhưng có suy đoán/bước thiếu căn cứ | Các bước trực tiếp phù hợp; không tự đổi expected để PASS |

Giữ rubric đang dùng: **đúng** khi `2+2`; **đúng một phần** khi tổng ít nhất 2 nhưng chưa `2+2`; **sai** khi tổng dưới 2. Nêu rõ suy đoán nào không có bằng chứng, không thưởng điểm chỉ vì trả lời dài. Không coi việc AI nhận diện sai khác actual/expected là xác nhận assertion đúng.

## Phiếu chưa chấm

Người chấm / vai trò / quan hệ với dự án: **Chưa có**. Ngày chấm và phiên bản dữ liệu: **Chưa ghi nhận**.

| ID mẫu | Nguyên nhân 0–2 | Bước kiểm tra 0–2 | Phân loại | Bằng chứng và nhận xét của người chấm |
| --- | --- | --- | --- | --- |
| AI-01 | — | — | Chưa chấm | — |
| AI-02 | — | — | Chưa chấm | — |
| AI-03 | — | — | Chưa chấm | — |
| AI-04 | — | — | Chưa chấm | — |
| AI-05 | — | — | Chưa chấm | — |
| AI-06 | — | — | Chưa chấm | — |
| AI-07 | — | — | Chưa chấm | — |
| AI-08 | — | — | Chưa chấm | — |
| AI-09 | — | — | Chưa chấm | — |
| AI-10 | — | — | Chưa chấm | — |

Không tính tổng hoặc tỷ lệ từ ô trống. Nếu một mẫu chưa đủ căn cứ, ghi “chưa chấm” và lý do, không tự quy thành 0. Lần AI-08 đầu trả HTTP 503 được ghi là lỗi dịch vụ; chấm câu trả lời retry đã lưu, không tính hai lần hoặc coi 503 là câu trả lời sai.

## Khi có phiếu hoàn tất

Giữ nguyên phiếu ban đầu, bổ sung bảng tổng hợp số mẫu thực sự được chấm và cả hai trục điểm. Nếu có hai người, báo cáo số mẫu đồng thuận/bất đồng trước thảo luận; lưu lý do và kết quả xử lý bất đồng riêng. Cập nhật [báo cáo thực nghiệm, mục 4.5](EXPERIMENT-REPORT.md#45-đánh-giá-ai) với người chấm, số mẫu, cách chấm và giới hạn; không ghi đè điểm sơ bộ cũ.

Bộ này chỉ có **1 lỗi HSK lịch sử và 9 lỗi có kiểm soát**, phần lớn không phải lỗi website phát hiện trong lượt mới. Alias model và thiếu modelVersion ở phần lớn phản hồi hạn chế khả năng tái lập. Ngay cả sau chấm độc lập, kết quả chỉ mô tả tập mẫu này; chưa đại diện cho độ chính xác Gemini trên mọi lỗi, chưa đo chất lượng gia sư AI HSK hay thời gian người dùng tiết kiệm.
