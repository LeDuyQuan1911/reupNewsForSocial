# Đọc cấu hình từ .env cục bộ

- Ngày: 2026-10-29
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cho dashboard, Hermes runner và các lệnh khởi động lấy cấu hình từ `.env` trong repo, để dễ chuyển sang máy server. Không đưa giá trị bí mật vào Git.

## Thực hiện
Thêm `app/local_env.py` và `scripts/load-env.ps1`; nạp file trước khi dashboard hoặc Hermes dùng cấu hình. Cập nhật lệnh cài/chạy Hermes, dịch vụ Windows và kiểm tra token Facebook để đọc `.env`. Tạo `.env` cục bộ từ các biến User hiện có mà không in giá trị hoặc đưa vào Git. Cập nhật `.env.example`, README, MAP, SPEC, PLAN và nhật ký quyết định.

## Quyết định
`.env` trong repo là nguồn ưu tiên; biến User Windows vẫn làm dự phòng để không làm hỏng máy đã cấu hình. Chỉ nạp khóa `REUP_*` và không in giá trị. `.env` bị Git bỏ qua; mẫu không có secret thật.

## Kiểm chứng
Ba unit test `test_local_env.py` qua; PowerShell parser báo cú pháp hợp lệ cho bảy script và nạp thành công `.env` cục bộ; `git check-ignore .env` xác nhận file được bỏ qua. Sau khi chuyển nạp file vào điểm khởi chạy `run.py`, toàn bộ 109 test qua với cấu hình CI giả; `scripts/cd/smoke.py` cũng qua. Chưa kiểm tra trên máy server vì công cụ đang ở máy phát triển.

## Còn lại
Trên máy server cần tạo `.env` riêng, điền key/token hợp lệ, rồi khởi động lại dashboard/Hermes và chạy phép kiểm tra kết nối. Không có quyền điều khiển trực tiếp máy server trong phiên này.
