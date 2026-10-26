# Thiết lập Hermes có thể mang theo repo

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Đưa cách cài và cấu hình Hermes dùng 9Router vào repo để chạy lại được trên máy Windows khác, không lưu API key hay dữ liệu cá nhân.

## Thực hiện
Thêm `scripts/setup-hermes.ps1` để xác minh SHA-256 installer, cài Hermes nếu chưa có, kiểm tra revision và đặt cấu hình model 9Router. Ban đầu script tải installer từ upstream; yêu cầu tiếp theo đã đưa toàn bộ source vào `vendor/hermes-agent/`, nên script hiện dùng installer vendored. Bổ sung hướng dẫn trong `README.md`, bản đồ trong `MAP.md`, yêu cầu trong `SPEC.md`, mốc trong `PLAN.md` và quyết định trong `contexte/decisions.md`.

## Quyết định
Không vendor runtime hoặc dữ liệu người dùng của Hermes. Script pin bản v0.22.5 đã chạy thử và chỉ lưu tên biến môi trường của API key trong cấu hình. Bản cài Hermes dùng chung trên máy ở revision khác sẽ không bị ghi đè.

## Kiểm chứng
Parser PowerShell không báo lỗi. Chạy `scripts/setup-hermes.ps1 -TestConnection` trên bản Hermes đã cài và chạy lại sau khi chuyển sang installer vendored: bốn mục cấu hình được đặt, model trả `OK`, mã thoát 0. Rà diff và không thêm secret.

## Còn lại
Chưa thử nhánh cài sạch trên máy thứ hai; máy đó cần Git, PowerShell, internet, 9Router và biến môi trường API key/model. Script không bật lịch Hermes hoặc tích hợp đăng Facebook.
