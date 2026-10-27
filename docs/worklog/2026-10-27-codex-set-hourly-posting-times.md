# Đặt lịch đăng theo giờ từ 06:00 đến 24:00

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn cập nhật trực tiếp số bài và các giờ đăng tự động từ 06:00 đến 24:00, không phải nhập thủ công.

## Thực hiện
Đã dùng `app.database.save_posting_settings` cập nhật dữ liệu cục bộ `data/reup.sqlite3` từ 12 lên 19 bài/ngày. Các mốc lưu là 00:00 và 06:00–23:00 theo giờ Bangkok. Không sửa source hoặc các bài đã xếp lịch.

## Quyết định
Ứng dụng chỉ nhận HH:MM trong 00:00–23:59 nên 24:00 được biểu diễn bằng 00:00 ngày hôm sau. Giao diện sẽ hiện 00:00 trong danh sách giờ. Đây là cập nhật cấu hình trên máy hiện tại, không đổi mặc định của repo cho máy khác.

## Kiểm chứng
Đọc lại cấu hình từ SQLite thấy `posts_per_day=19` và đúng 19 mốc. Gọi `automation.next_slot` tại 23:30 Bangkok cho kết quả 00:00 ngày kế tiếp.

## Còn lại
Các bài đã được xếp lịch giữ nguyên; cấu hình mới áp dụng cho bài được xếp sau thời điểm cập nhật.
