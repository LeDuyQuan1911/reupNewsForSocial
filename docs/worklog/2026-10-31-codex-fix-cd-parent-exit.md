# Sửa CD khi launcher Python tự thoát

- Ngày: 2026-10-31
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Máy server không triển khai commit mới dù CI xanh; xác định lỗi và sửa script CD Windows để cập nhật an toàn.

## Thực hiện
Kiểm tra kết quả chạy thực tế trên server: `-CheckOnly` nhận CI nhưng chạy triển khai thất bại khi dừng PID dashboard. Sửa `scripts/cd/update-server.ps1` để giữ handle của launcher và tiến trình con đã xác minh, chấp nhận launcher Python tự thoát sau tiến trình con, và chỉ tiếp tục khi cả hai đã dừng. Thêm test mô phỏng trường hợp launcher tự thoát, PID con bị dùng lại và lỗi truy vấn CIM.

## Quyết định
Giữ kiểm tra tiến trình thuộc dashboard và cổng 5000. Dùng handle tiến trình thay cho lệnh dừng theo PID sau bước xác minh; tránh dừng nhầm tiến trình được Windows cấp lại PID. Lỗi CIM làm dừng triển khai.

## Kiểm chứng
Ba test mô phỏng trong `test_cd_dashboard_stop.py` đạt; test parse toàn bộ script bằng Windows PowerShell 5.1 đạt. `git diff --check` sạch. Review độc lập ban đầu tìm hai rủi ro; sau sửa bổ sung reviewer rút lại cả hai và không có phát hiện mới. Chưa thử deploy thật trên server.

## Còn lại
Cần mở PR, chờ CI/merge theo quyết định chủ repo rồi thử lại CD trên server. Task CD trên server đang Disabled để tránh retry lỗi; dashboard và Hermes vẫn chạy. Không có thay đổi secrets hay dữ liệu SQLite trong branch này.
