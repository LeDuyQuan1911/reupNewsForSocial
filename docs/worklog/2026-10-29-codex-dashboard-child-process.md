# Sửa updater nhận tiến trình con Python trên Windows

- Ngày: 2026-10-29
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Trên server, updater báo dashboard health thất bại dù Flask trả OK vì PID file trỏ launcher Python `.venv` còn cổng 5000 thuộc tiến trình Python con. Sửa kiểm tra/đóng dashboard an toàn trước khi cài updater.

## Thực hiện
Trên server, người dùng đối chiếu `dashboard.pid` (PID 11032 của `.venv` launcher) với listener 127.0.0.1:5000 (PID 9660, con trực tiếp của 11032, `python.exe -u run.py`); `/healthz` trả OK. Sửa `scripts/cd/update-server.ps1` để nhận listener thuộc launcher hoặc con Python trực tiếp có command line `run.py`; dừng con trước launcher khi cập nhật, dọn tiến trình nếu health thất bại, tăng thời gian chờ. Cập nhật PLAN và quyết định kỹ thuật.

## Quyết định
Chỉ nhận/dừng con trực tiếp của launcher đã xác minh thuộc `.venv` và command line `run.py`; từ chối nếu cổng 5000 do tiến trình khác giữ.

## Kiểm chứng
PowerShell 5.1 parse script và regex nhận `python.exe -u run.py`; 111 unit test và dashboard smoke check qua; `git diff --check` sạch. Chưa thử updater bản sửa trên server trước khi merge.

## Còn lại
Cần PR, CI/review và merge do chủ repo quyết định. Server đang có dashboard trả `/healthz` OK dù `-StartOnly` cũ báo timeout; chưa cài task updater, chưa bật đăng tự động và Facebook token vẫn trống.
