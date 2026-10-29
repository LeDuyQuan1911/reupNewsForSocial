# CI/CD cho máy chủ Windows

## Luồng phát hành

1. Mở PR vào `main`. GitHub Actions chạy `Python tests (Windows)` trên runner tạm, với token rỗng và tự động đăng tắt. PR được kiểm tra trên merge ref của GitHub.
2. Ruleset `main` yêu cầu check trên và yêu cầu nhánh PR cập nhật với `main`. Chủ repo xem review rồi quyết định merge.
3. Commit thực tế trên `main` chạy CI lần nữa. Nếu thất bại, commit vẫn ở `main` nhưng máy chủ không nhận nó.
4. Task Scheduler trên máy chủ gọi `scripts/cd/update-server.ps1` mỗi 5 phút. Script fetch `main`, yêu cầu đúng SHA đó có lượt CI **push** thành công, rồi mới cập nhật. Lượt CI của PR không đủ điều kiện.
5. Script tạm dừng cron Hermes, đợi lượt đang chạy, dừng dashboard do nó quản lý, sao lưu SQLite, checkout đúng SHA, cài phụ thuộc và kiểm tra bằng DB tạm. Dashboard mới chỉ phục vụ `/healthz` trong lúc cập nhật, các thao tác khác nhận 503. Sau khi health check đạt, script cập nhật runner Hermes và tiếp tục cron. Nếu bước trước khi thử tiếp tục cron lỗi, script phục hồi code và DB từ bản sao rồi chạy lại bản cũ. Nếu đã thử tiếp tục cron, script giữ trạng thái bảo trì và yêu cầu đối chiếu thủ công thay vì ghi đè DB.

Không có cơ chế bỏ qua CI khi GitHub API không truy cập được. `data/`, `.venv/` và `.env` cục bộ không nằm trong Git; checkout mã nguồn không thay chúng. Bản sao SQLite lưu trong `data/backups/` trên máy chủ. Sự cố sau khi đã thử tiếp tục cron cần đối chiếu thủ công với Facebook để tránh đăng trùng.

## Kích hoạt CI trên GitHub

Ruleset [#25950396](https://github.com/LeDuyQuan1911/reupNewsForSocial/rules/25950396) đã bật trên GitHub ngày 2026-10-27 và yêu cầu `Python tests (Windows)` cùng trạng thái cập nhật với `main`. File `governance/github-main-ruleset.json` là bản cấu hình mong muốn; chỉnh file này không tự đồng bộ lên GitHub. Workflow đang chạy trên PR #3 và chỉ chạy trên `main` sau khi chủ repo merge. Kiểm tra lại ruleset trên GitHub khi đổi tên job hoặc workflow.

## Cài trên máy chủ Windows sau này

1. Cài Git, Python 3.12+, 9Router và Hermes theo README. Dùng một tài khoản Windows riêng, không dùng checkout đang phát triển. Clone `https://github.com/LeDuyQuan1911/reupNewsForSocial.git` vào đường dẫn cố định; máy này chỉ chạy mã từ `main`.
2. Tại repo máy chủ, tạo `.venv`, cài `requirements.txt`, chép riêng `.env` vào gốc checkout và điền key 9Router cùng thông tin Page của máy chủ. `.env` là file cục bộ được Git bỏ qua; không stage, commit hoặc đưa token vào chat. Tạo/cấu hình SQLite và Hermes theo README; xác nhận `data/hermes-automation.enabled` và `data/hermes-cron-job-id.txt` đã tồn tại.
3. Dừng mọi dashboard đang chạy thủ công trên cổng 5000. Chạy `powershell -File scripts/cd/update-server.ps1 -CheckOnly` để xác minh origin, cây Git sạch và CI của commit mới. Khi checkout đã ở đúng SHA của `main` với CI xanh, chạy `powershell -File scripts/cd/update-server.ps1 -StartOnly` để updater quản lý dashboard và ghi `data/dashboard.pid`. Không để hai dashboard cùng chạy.
4. Chạy `powershell -File scripts/cd/install-updater.ps1` bằng **chính tài khoản đang chạy Hermes**. Script hỏi mật khẩu tài khoản Windows qua hộp thoại an toàn, tạo Scheduled Task chạy kể cả khi đã đăng xuất và kiểm tra mỗi 5 phút. Kiểm tra Task Scheduler → History và chạy `Get-ScheduledTask -TaskName 'reupNewsForSocial update'`.
5. Kiểm tra dashboard, trạng thái Hermes và một lần xử lý thử có kiểm soát trước khi bật tự đăng. Đặt lịch sao lưu ngoài máy chủ cho `data/`; bản sao trước mỗi deploy không thay thế backup định kỳ.

Nếu server đang dùng một dashboard cũ do script khác mở, updater sẽ dừng thay đổi thay vì giết tiến trình lạ. Dừng dashboard đó một lần và để updater quản lý các lần chạy sau. Nếu cần vô hiệu tự cập nhật, Disable task trong Task Scheduler. Khi cập nhật lỗi, xem output/Last Run Result và `data/deployment-paused`; nếu marker còn lại, xử lý lỗi và đối chiếu trước khi cho Hermes chạy lại.
