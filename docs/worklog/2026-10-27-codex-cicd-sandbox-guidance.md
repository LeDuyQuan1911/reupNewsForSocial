# Giải thích môi trường thử nghiệm CI/CD

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích có cần sandbox để thử code trước khi máy server tự nhận bản mới hay không; chưa triển khai pipeline.

## Thực hiện
Đối chiếu tài liệu GitHub về runner tạm thời và an toàn của self-hosted runner với kiến trúc repo hiện tại (Flask, Hermes, 9Router, SQLite, Facebook Page).

## Quyết định
Đề xuất CI trên GitHub-hosted runner tách biệt và thêm kiểm tra bản mới trên máy server với SQLite tạm, cấu hình giả, tắt Hermes cron và không gửi Facebook trước khi chuyển bản thật. Máy staging riêng chỉ cần khi yêu cầu kiểm thử tích hợp đầy đủ hoặc rủi ro triển khai tăng.

## Kiểm chứng
Đọc tài liệu GitHub chính thức về runner mới cho mỗi job và cảnh báo runner tự host trên repo công khai. Không chạy test vì không đổi code.

## Còn lại
Chưa có pipeline hoặc sandbox; cần triển khai sau khi người dùng chốt luồng cập nhật.
