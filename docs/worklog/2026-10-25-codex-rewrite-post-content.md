# Viết lại nội dung bài đăng

- Ngày: 2026-10-25
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn nội dung bài đăng được viết lại, không chỉ thêm ảnh; kiểm tra và chỉnh bài số 6 đang mở trên dashboard, giữ chế độ thử nghiệm không đăng.

## Thực hiện
Kiểm tra bài số 6 trong SQLite và bài gốc của OpenAI; dùng model 9Router đã cấu hình để tạo nội dung tiếng Việt mới từ các dữ kiện được xác minh, rồi lưu nội dung vào bài số 6. Giữ nguyên hai ảnh, trạng thái đã lên lịch thử nghiệm và cờ `test_only=1`. Không thay đổi source code.

## Quyết định
Sửa trực tiếp nội dung bài thử trong SQLite bằng điều kiện `status='scheduled' AND test_only=1` để giữ lịch và bảo đảm không động đến bài đang đăng thật. Bài gốc được dùng để đối chiếu dữ kiện, không chép nguyên văn.

## Kiểm chứng
Sau khi lưu, `GET /posts/6` trả HTTP 200; nội dung mới hiển thị, nhãn lịch thử nghiệm còn hiện và có hai liên kết ảnh. Kiểm tra trước cập nhật xác nhận hai file ảnh vẫn tồn tại.

## Còn lại
Nội dung đã được viết lại nhưng chưa kiểm duyệt lại bằng model vision; bài thử không được gửi Facebook. Không có Page ID/token để thử xuất bản thật.
