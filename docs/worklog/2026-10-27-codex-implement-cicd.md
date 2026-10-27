# Triển khai CI/CD cho máy chủ Windows

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thiết lập kiểm tra PR và commit trên `main`, chuẩn bị cơ chế máy chủ Windows tự lấy đúng commit đã qua CI. Chưa cài lên máy chủ vì máy đó chưa cần thiết lập.

## Thực hiện
Giữ CI Windows cho PR và `main`, thêm smoke check DB tạm. Thêm `scripts/cd/release_gate.py` để chỉ chấp nhận đúng SHA có workflow `push` thành công; test trường hợp PR, nhánh khác, CI lỗi và rerun thất bại. Thêm script Windows tự cập nhật, tạm dừng Hermes, khóa lượt chạy, sao lưu/phục hồi SQLite, kiểm tra HTTP và giữ dữ liệu/ảnh ngoài Git. Thêm script cài Scheduled Task và hướng dẫn `docs/deployment.md`. Cập nhật ruleset mong muốn, README, MAP, SPEC, PLAN, governance và quyết định kỹ thuật.

## Quyết định
Máy server sẽ tự poll GitHub mỗi 5 phút bằng tài khoản Windows sở hữu Hermes. Chỉ triển khai commit `main` với lượt CI `push` thành công; lỗi API hoặc checkout bẩn thì dừng. Không dùng máy server làm runner cho PR.

## Kiểm chứng
95/95 unit test đạt với cấu hình CI giả; smoke dashboard dùng DB tạm đạt. YAML CI và JSON ruleset parse được; hai script PowerShell parse được; `git diff --check` đạt. GitHub API hiện trả danh sách ruleset rỗng cho repo này. Chưa chạy end-to-end trên máy server vì chưa cài máy đó.

## Còn lại
Workflow CI đang là file chưa commit và chưa chạy trên GitHub; cần đưa lên PR, review độc lập, chủ repo merge rồi áp dụng ruleset sau check đầu tiên. Khi có máy Windows server, clone repo và cài Hermes/9Router, đặt biến môi trường User, chạy bootstrap và cài Scheduled Task theo `docs/deployment.md`. Dữ liệu ảnh cần backup riêng; script phục hồi chỉ áp dụng trước khi tiếp tục cron.
