# Chạy bản xem thử thiết lập Hermes

- Ngày: 2026-11-01
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Chạy giao diện web của nhánh thiết lập nội dung để chủ dự án xem thử trên máy hiện tại.

## Thực hiện
Khởi động Flask từ worktree `codex/web-content-settings` tại `127.0.0.1:5012` với SQLite xem thử trong worktree. Không chạy các thread scheduler/automation của `run.py`.

## Quyết định
Dùng cổng 5012 và cơ sở dữ liệu riêng để bản xem thử không can thiệp dữ liệu hoặc lịch đăng của máy server.

## Kiểm chứng
GET `/hermes` trả HTTP 200; HTML chứa form số bài/giờ đăng, giới hạn ứng viên, phong cách viết và ưu tiên tìm tin.

## Còn lại
Server xem thử chỉ tồn tại trong phiên hiện tại. Thiết lập trên máy server chưa được nạp vào cơ sở dữ liệu này; PR #12 chưa merge.
