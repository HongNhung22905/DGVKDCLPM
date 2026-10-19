# Tạo Neon branch riêng cho kiểm thử HSK

Database trong `hsk-app/frontend/.env.local` đang phục vụ website hiện tại và chưa được phép ghi/xóa khi kiểm thử. Hướng dẫn này dùng kết nối riêng ở `ai-test-tool/.env.hsk-test`; giữ nguyên kết nối website hiện tại.

## 1. Tạo branch trên Neon Console

1. Mở [Neon Console](https://console.neon.tech/), chọn project chứa database HSK.
2. Chọn **Branches → New branch**. Chọn branch đang chứa schema HSK làm nguồn.
3. Đặt tên **hsk-test-2026-10-19** (hoặc tên bắt đầu bằng `hsk-test-`).
4. Ở phần dữ liệu, chọn **Schema only** để sao chép cấu trúc bảng mà không sao chép tài khoản/dữ liệu thật. Các test hiện tại tự tạo tài khoản; nội dung từ vựng/tìm kiếm được đọc từ tệp của HSK.
5. Chọn thời hạn tự xóa phù hợp với đợt kiểm thử, rồi bấm **Create**. Nếu Console không cho tạo schema-only do giới hạn tài khoản, dừng ở đây và báo lại; chưa dùng kết nối website hiện tại để thay thế.
6. Mở **Connect**, chọn đúng branch `hsk-test-…`, database và role của branch đó. Sao chép chuỗi kết nối PostgreSQL. Giữ các tham số SSL Neon cung cấp.

Các bước và lựa chọn Schema only theo [hướng dẫn quản lý branch](https://neon.com/docs/manage/branches) và [schema-only branch](https://neon.com/docs/guides/branching-schema-only) của Neon. Việc sửa dữ liệu ở branch riêng không sửa dữ liệu branch nguồn. Không đặt branch test làm default và không thay biến môi trường deployment của website.

## 2. Điền file cấu hình riêng trên máy

File `ai-test-tool/.env.hsk-test` chứa cấu hình riêng trên máy. Khi thiết lập môi trường mới, điền theo mẫu sau:

```dotenv
HSK_TEST_BRANCH=hsk-test-2026-10-19
HSK_TEST_DATABASE_HOST=ep-HOST-CUA-BRANCH-MOI.REGION.aws.neon.tech
DATABASE_URL=postgresql://ROLE:PASSWORD@ep-HOST-CUA-BRANCH-MOI.REGION.aws.neon.tech/DATABASE?sslmode=require
NEXTAUTH_SECRET=
```

Đây là ví dụ có placeholder, không phải URL sử dụng được. Dán **chuỗi thực tế Neon cấp cho branch mới**; nếu hostname có `-pooler`, dùng hostname đó cho cả hai dòng. Không tự đoán hostname. Để trống `NEXTAUTH_SECRET` để công cụ tạo secret riêng cho phiên kiểm thử.

File này được Git bỏ qua. Không dán mật khẩu hoặc connection string vào chat. Không sửa `hsk-app/frontend/.env.local`, cấu hình Vercel hay kết nối branch hiện tại.

## 3. Mở HSK kiểm thử

Từ thư mục gốc repo:

```powershell
npm --prefix ai-test-tool run hsk:test
```

Lệnh này kiểm tra URL/hostname/SSL và từ chối endpoint trùng database hiện tại, kể cả URL pooled/unpooled khác nhau. Nếu cấu hình thiếu thì dừng trước khi mở ứng dụng hoặc kết nối DB.

Khi cấu hình hợp lệ, công cụ chụp mã HSK sang `ai-test-tool/data/hsk-test-app/<id>/`, bỏ qua các tệp `.env*`, build cũ và dependency. Snapshot dùng dependency đã cài của HSK, chạy Next với `DATABASE_URL` test trong tiến trình riêng và sinh build trong snapshot. Không thay đổi kết nối hay mã nguồn HSK gốc. Mỗi snapshot khoảng 62 MB tại thời điểm thiết lập.

Mở **http://localhost:3000/login**. Nếu cổng 3000 đang có server khác, tự dừng server local đó trước; launcher không tự đóng nó. Giữ terminal này chạy trong suốt đợt Selenium.

Schema-only branch đã có schema nguồn, nên chưa cần chạy migration/reset/database seed. Nếu xuất hiện thiếu bảng hoặc lệch schema, lưu lỗi và đối chiếu schema trước; không chạy lệnh reset trên database website.

## 4. Mở công cụ và chạy nhóm nhỏ trước

Trong terminal thứ hai:

```powershell
npm --prefix ai-test-tool start
```

Mở **http://localhost:4317 → Selenium → Tra từ và sổ tay → Chạy kiểm thử**. Nhóm này gồm 10 ca. Runner chỉ cho chạy Selenium khi nhận đúng marker từ HSK kiểm thử do launcher trên tạo ra; một website bất kỳ ở cổng 3000 không đủ điều kiện.

Lưu XML, nhật ký, thời gian và ảnh ở `ai-test-tool/data/runs/<id>/`. Sau khi 10 ca này hoàn tất và đối chiếu XML đúng, mới chạy **Toàn bộ Selenium** (85 ca đã thu thập ở phiên trước; cần thu thập lại nếu mã test thay đổi).

Khi xong, dùng Ctrl+C để dừng từng terminal. Đừng xóa branch trong lúc test còn chạy. Chưa có lệnh nào trong hướng dẫn này yêu cầu sửa/xóa dữ liệu trên branch website hiện tại.

## Trạng thái hiện tại

Đã cấu hình endpoint kiểm thử riêng và kiểm tra khác endpoint website hiện tại. Kết nối chỉ đọc ban đầu xác nhận 12 bảng, có `User` và `NotebookEntry`, số tài khoản lúc kiểm tra là 0. HSK snapshot đã khởi động thành công và nhóm tìm kiếm/sổ tay chạy qua UI đạt 10/10 PASS, khớp XML gốc. Các lượt sau tạo tài khoản/dữ liệu tổng hợp trên endpoint kiểm thử này.

Launcher đã được sửa để đặt thư mục làm việc vào snapshot trước khi chuẩn bị Next, vì HSK đọc `public/data` và Tailwind theo thư mục hiện tại. Lượt đầu gặp lỗi đường dẫn đã được dừng và lưu riêng; không cộng lượt đó vào kết quả nhóm 10 ca. Xem [báo cáo thực nghiệm](EXPERIMENT-REPORT.md) để biết kết quả mới nhất.
