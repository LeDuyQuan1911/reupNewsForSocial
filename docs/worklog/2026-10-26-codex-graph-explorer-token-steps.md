# Hướng dẫn lấy Page token trong Graph API Explorer

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Chỉ đúng thao tác lấy Facebook Page access token từ màn hình Meta Graph API Explorer người dùng cung cấp.

## Thực hiện
Đối chiếu ảnh chụp giao diện đang mở với Page ID và script cấu hình của repo; hướng dẫn tạo User token, gọi `/me/accounts`, chọn Page token đúng ID và nhập kín trên máy. Không lấy hoặc lưu token từ ảnh.

## Quyết định
Ưu tiên thao tác trực tiếp trong Meta App hiện có. Phân biệt User token ở panel phải và Page token trong phản hồi `/me/accounts`; yêu cầu che token khi chia sẻ ảnh.

## Kiểm chứng
Ảnh cho thấy App CreatePost, Graph API v26.0, loại Mã người dùng và các quyền `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`. Script repo kiểm tra tên/ID Page trước khi lưu token.

## Còn lại
Chủ tài khoản cần bấm cấp quyền trong Meta và nhập Page token vào script; không có thay đổi code trong nhiệm vụ này.
