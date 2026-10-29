# Sửa script PowerShell 5.1 đọc UTF-8

- Ngày: 2026-10-29
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Sửa lỗi parser Windows PowerShell 5.1 trên máy server khi cài Hermes cron; đảm bảo script có chữ tiếng Việt đọc đúng và có kiểm tra phòng hồi quy.

## Thực hiện
Trên máy server, `install-hermes-automation.ps1` dừng ở parser với chữ tiếng Việt bị giải mã sai. Trên nhánh riêng từ `main`, thêm UTF-8 BOM cho bốn script có tiếng Việt chưa có BOM (`configure-facebook-page`, `install-hermes-automation`, `start-hermes`, `start-local-services`). Thêm `tests/test_powershell5_syntax.py`; cập nhật MAP, SPEC, PLAN và quyết định kỹ thuật.

## Quyết định
Dùng UTF-8 BOM cho script có ký tự ngoài ASCII để Windows PowerShell 5.1 đọc đúng. Không thêm phụ thuộc PowerShell 7 trên server.

## Kiểm chứng
Trước sửa, parser của `powershell.exe` báo lỗi ở bốn script. Sau sửa, PowerShell 5.1 parse được cả 10 script; 110 unit test và dashboard smoke check qua. `git diff --check` sạch.

## Còn lại
Đẩy nhánh, mở PR, đợi CI/review và chủ repo merge; server kéo commit mới rồi chạy lại lệnh cài Hermes cron. Facebook token vẫn chưa có, tự động đăng vẫn tắt.
