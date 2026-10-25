# Bài viết có ảnh

- Ngày: 2026-10-25
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng cần có ít nhất một bài viết kèm ít nhất một ảnh, có thể dùng ảnh bài gốc, ảnh chụp repo hoặc ảnh tổng hợp được tạo tự động.

## Thực hiện
Kiểm tra `app/media.py`, `app/database.py`, `app/automation.py`, giao diện biên tập và dữ liệu SQLite. Có 16 bài đăng, cả 16 đều có ảnh trong `post_images` và file ảnh còn tồn tại. Bài số 6 đã được AI viết lại, có một ảnh AI và một ảnh thẻ tiêu đề; bài đang ở lịch thử nghiệm, không gửi Facebook. Mở trang xem trước bài số 6 trong Codex.

## Quyết định
Chưa cần sửa code: luồng hiện tại đã ưu tiên ảnh nguồn/chụp repo và tạo ảnh thẻ tiêu đề khi không lấy được ảnh; khâu lên lịch và gửi yêu cầu ít nhất một ảnh. Dùng bài số 6 làm ví dụ có thể kiểm tra ngay.

## Kiểm chứng
`GET /posts/6` trả HTTP 200; cả hai endpoint ảnh của bài trả HTTP 200 và `image/jpeg`. Đối chiếu SQLite: 16 bài đăng, 0 bài không có bản ghi ảnh; file ảnh của cả 16 bài còn tồn tại.

## Còn lại
Ảnh thẻ tiêu đề là ảnh dự phòng tạo từ dữ kiện bài, không phải ảnh AI. Bài số 6 đang trong lịch thử nghiệm nên không được đăng lên Facebook.
