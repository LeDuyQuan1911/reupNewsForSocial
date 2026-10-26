# Thiết lập Hermes Agent dùng 9Router

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cài Hermes Agent trên máy Windows, cấu hình Custom endpoint tới 9Router localhost, thử một lượt gọi model. Chưa tích hợp đăng Facebook hay bật lịch Hermes.

## Thực hiện
Cài Hermes Agent stable v0.22.5 trên Windows vào thư mục dữ liệu người dùng. Khắc phục junction Python do `uv` tạo bị lỗi khi cài, rồi hoàn tất installer. Cấu hình Hermes dùng endpoint 9Router localhost và model nhẹ đã dùng trong dự án. Không sửa mã ứng dụng; file repo duy nhất của nhiệm vụ là nhật ký này.

## Quyết định
Dùng bản Windows native để Hermes chạy trên cùng máy với 9Router. Cấu hình `model.key_env` tham chiếu tên biến môi trường Windows đã có, không chép API key vào cấu hình hay repo. Giữ Hermes ở chế độ chạy thủ công; chưa bật lịch hay đăng Facebook.

## Kiểm chứng
`node scripts/plugins.mjs check`: cấu hình plugin hợp lệ. `hermes config get` xác nhận model, provider custom, endpoint và tên biến môi trường. 9Router lắng nghe ở cổng 20128. `hermes -z 'Reply with exactly: OK'`: trả `OK`, mã thoát 0. `git status --short`: chỉ có nhật ký mới của nhiệm vụ này bên cạnh các thay đổi có trước.

## Còn lại
Chưa cấu hình lịch tự động, công cụ tìm bài hoặc quyền đăng Facebook; đó là các bước riêng cần thiết trước khi hệ thống tự đăng. Không có giới hạn khác cho việc cài và gọi thử model.
