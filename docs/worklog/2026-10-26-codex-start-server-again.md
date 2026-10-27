# Khởi động server cục bộ

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Kiểm tra và khởi động dashboard cục bộ để người dùng xem ứng dụng ở localhost.

## Thực hiện
Đã kiểm tra cổng 5000 và 20128 đều chưa lắng nghe, sau đó chạy `scripts/start-local-services.ps1`. Dashboard và 9Router đều khởi động trên localhost.

## Quyết định
Dùng script sẵn có của repo để nạp biến môi trường User và tránh tạo tiến trình trùng.

## Kiểm chứng
`GET http://127.0.0.1:5000/` trả HTTP 200. Cổng 20128 của 9Router đã chuyển sang trạng thái lắng nghe sau vài giây.

## Còn lại
Không có.
