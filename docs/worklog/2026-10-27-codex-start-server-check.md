# Kiểm tra và mở server cục bộ

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn chạy server của repo để truy cập dashboard. Kiểm tra thêm dịch vụ 9Router cần cho chức năng AI.

## Thực hiện
Xác nhận dashboard Python đã nghe cổng 5000 nên giữ tiến trình hiện có. Chạy `scripts/start-local-services.ps1` để mở 9Router đang tắt; không sửa source hoặc cấu hình.

## Quyết định
Giữ dashboard đang chạy để không ngắt phiên người dùng. Mở thêm 9Router vì ứng dụng dùng endpoint cục bộ này cho các bước AI.

## Kiểm chứng
`http://127.0.0.1:5000/` và `/hermes` trả HTTP 200. 9Router nghe cổng 20128 và `/login` trả HTTP 200.

## Còn lại
Không có. Chưa gọi model AI hoặc đăng thử bài vì yêu cầu chỉ là mở server.
