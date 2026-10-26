# Đưa source Hermes vào repo

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Đưa mã nguồn open source Hermes đã cài vào repo để thấy được code khi mang dự án sang máy khác, đồng thời đánh giá ảnh hưởng.

## Thực hiện
Chép 20.799 file được upstream theo dõi ở commit `bf0203a794a07aac3ff764972ab9087baa4e4f4e` vào `vendor/hermes-agent/`. Giữ `LICENSE`; không chép `.git`, `node_modules`, cache, phiên và secrets. Cập nhật `scripts/setup-hermes.ps1` dùng installer vendored. Cập nhật README, MAP, SPEC, PLAN, quyết định và `.gitattributes` để giữ byte của một file CRLF đặc biệt. Snapshot, script và `.gitattributes` đã được commit cục bộ ở `f6580c59`; chưa push.

## Quyết định
Giữ trọn snapshot upstream, bao gồm license MIT; runtime vẫn được cài riêng trên từng máy. Repo tăng 20.799 file và khoảng 221,6 MB blob. Installer vendored được kiểm tra SHA-256; script không ghi đè bản Hermes dùng chung ở commit khác.

## Kiểm chứng
So sánh Git tree hash của toàn bộ vendor với commit upstream: cùng `79cfdac56f6c46036c319172fd39678fb8f0c472`, kể cả 107 file có quyền thực thi. Parser PowerShell hợp lệ; `scripts/setup-hermes.ps1 -TestConnection` trả `OK`, mã thoát 0. Worklog được kiểm tra bằng `node scripts/check-worklog.mjs`.

## Còn lại
Chưa thử cài sạch trên máy thứ hai; máy mới vẫn cần Git, internet để tải dependencies, 9Router và key riêng. Clone/duyệt diff sẽ nặng hơn, nâng Hermes sau này cần cập nhật snapshot. Chưa push.
