# Giải thích thời hạn Facebook Page token

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích liệu chủ dự án có phải lấy Page token mới mỗi ngày và cách giảm việc cấp lại thủ công.

## Thực hiện
Đối chiếu lỗi thực tế 190/463 của token đang lưu với tài liệu token Page của Meta; kiểm tra quy trình lấy token qua User token và `/me/accounts`. Không thay đổi mã hay cấu hình.

## Quyết định
Khuyên dùng Page token lấy từ User token dài hạn và kiểm tra hạn bằng Access Token Debugger; không hứa token tồn tại vĩnh viễn vì Meta có thể thu hồi hoặc quyền thay đổi.

## Kiểm chứng
Meta Graph API thực tế xác nhận token hiện tại đã hết hạn. Tài liệu Meta trên Postman xác nhận `/me/accounts` trả Page access token tương ứng. Không chạy lệnh sửa cấu hình.

## Còn lại
Cần chủ tài khoản đăng nhập Meta để cấp token mới; chưa có token hợp lệ để kiểm tra loại/hạn thực tế trên máy.
