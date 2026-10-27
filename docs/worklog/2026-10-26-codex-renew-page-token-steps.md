# Các bước thay Page token đã hết hạn

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Chỉ dẫn cụ thể bước tiếp theo để cấp lại Page access token cho Page đang cấu hình và khôi phục xác minh trên dashboard.

## Thực hiện
Kiểm tra Page ID, phiên bản Graph API cục bộ và script nhập token. Đối chiếu luồng lấy Page token qua Meta App và `/me/accounts` với tài liệu Meta. Không sửa cấu hình hay đọc/in giá trị token.

## Quyết định
Chủ tài khoản thực hiện bước đăng nhập/cấp quyền trong Meta; token mới được nhập trực tiếp bằng script PowerShell có đầu vào ẩn. Dùng đúng Page ID đang cấu hình; kiểm tra lại thời hạn token bằng Access Token Debugger.

## Kiểm chứng
Page ID hiện cấu hình là 342796135574782, phiên bản Graph API là v26.0. Script xác minh tên/ID Page trước khi lưu và yêu cầu khởi động lại dashboard.

## Còn lại
Cần chủ tài khoản cấp token mới trong Meta; token hết hạn không thể được xác minh lại bằng ứng dụng hiện tại. Không có thay đổi code trong nhiệm vụ này.
