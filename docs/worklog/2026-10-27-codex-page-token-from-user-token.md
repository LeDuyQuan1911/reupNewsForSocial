# Lấy Page token khi Graph Explorer không hiện kết quả

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng bấm Gửi trong Graph API Explorer nhưng khung phản hồi trống; cần cách lấy Page access token của Page đã chọn mà không lộ token.

## Thực hiện
Bổ sung `-FromUserToken` cho `scripts/configure-facebook-page.ps1`: nhập User token bằng lời nhắc ẩn, gọi Graph API theo Page ID đã lưu, xác minh Page token trả về rồi lưu cấu hình vào biến môi trường User. Cập nhật cách dùng trong `README.md` và mô tả script trong `MAP.md`.

## Quyết định
Khung phản hồi Graph API Explorer trống không đủ dữ kiện kết luận nguyên nhân. Gọi API Page trực tiếp trên máy để người dùng không cần lấy token từ khung phản hồi; không lưu User token. Giữ nguyên đường cấu hình Page token cũ và chế độ `-Check`.

## Kiểm chứng
PowerShell Parser: không có lỗi cú pháp. Kiểm tra hai chế độ xung đột: đúng thông báo lỗi. `git diff --check`: không có lỗi khoảng trắng. Chưa thử gọi Meta thật vì không lấy User token từ người dùng hoặc trình duyệt.

## Còn lại
Người dùng cần chạy script và dán User token trong lời nhắc ẩn. Sau khi lưu Page token, cần khởi động lại dashboard và thử đăng một bài có kiểm soát; quyền đọc không chứng minh quyền đăng. Hạn token mới phụ thuộc loại User token đã tạo.
