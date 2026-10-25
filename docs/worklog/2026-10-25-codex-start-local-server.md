# Khởi động server cục bộ

- Ngày: 2026-10-25
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn khởi động server để kiểm tra trang workflow trên localhost. Kiểm tra và khởi động dashboard cùng 9Router theo script hiện có.

## Thực hiện
Đọc hướng dẫn repo, trạng thái Git và script `scripts/start-local-services.ps1`; chạy script để bật dashboard và 9Router trên localhost. Không thay đổi source.

## Quyết định
Sử dụng script khởi động dịch vụ sẵn có của dự án.

## Kiểm chứng
Xác nhận `GET http://127.0.0.1:5000/workflow` trả HTTP 200; cổng 5000 và 20128 đều ở trạng thái lắng nghe. Lần kiểm tra trong sandbox bị chặn quyền socket, nên xác nhận bằng lệnh ngoài sandbox.

## Còn lại
Không có.
