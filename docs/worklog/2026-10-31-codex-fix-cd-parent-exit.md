# Sửa CD khi launcher Python tự thoát

- Ngày: 2026-10-31
- Agent: Codex
- Trạng thái: đang làm

## Yêu cầu và phạm vi
Máy server không triển khai commit mới dù CI xanh; xác định lỗi và sửa script CD Windows để cập nhật an toàn.

## Thực hiện
Kiểm tra kết quả chạy thực tế trên server: `-CheckOnly` nhận CI nhưng chạy triển khai thất bại khi dừng PID dashboard. Sửa `scripts/cd/update-server.ps1` để chấp nhận launcher Python tự thoát sau tiến trình con; xác minh PID chưa bị tái sử dụng và launcher thực sự đã dừng trước khi tiếp tục.

## Quyết định
Giữ kiểm tra tiến trình thuộc dashboard và cổng 5000. Chỉ bỏ điều kiện coi launcher tự thoát là lỗi, không bỏ bước xác minh dừng tiến trình.

## Kiểm chứng
Chưa chạy kiểm tra sau sửa.

## Còn lại
Cần chạy kiểm tra PowerShell, review độc lập và thử lại CD trên server. Không có thay đổi secrets hay dữ liệu SQLite trong branch này.
