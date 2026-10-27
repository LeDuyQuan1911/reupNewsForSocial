# Đẩy thay đổi và chạy CI/CD

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Đưa thay đổi hiện tại của repo lên GitHub, chạy CI qua PR và bật cổng CI cho `main`. Máy chủ Windows chưa cần cài đặt.

## Thực hiện
Tạo nhánh `codex/cicd-rollout`, commit và push mã ứng dụng cùng CI/CD lên GitHub; mở PR #3. CI Windows ban đầu phát hiện thiếu `tzdata`, đã thêm dependency và chạy lại. Review độc lập phát hiện rủi ro rollback ghi đè trạng thái bài vừa đăng; thêm chế độ bảo trì dashboard và ranh giới không tự rollback sau khi thử tiếp tục Hermes. Tích hợp report review hai lượt. Bật ruleset GitHub #25950396 yêu cầu check `Python tests (Windows)` mới nhất với `main`.

## Quyết định
Giữ PR mở cho chủ repo quyết định merge theo governance. Không cài Scheduled Task/CD trên máy server vì người dùng muốn để sau. Không đưa worklog cũ còn dang dở vào commit.

## Kiểm chứng
Rà soát staged diff và mẫu secrets: không phát hiện token/key thật; `git diff --check` đạt. Test cục bộ 96/96 đạt với biến môi trường CI; smoke dashboard và cú pháp PowerShell đạt. GitHub Actions trên PR #3 xanh ở commit `ceb842d9`; reviewer độc lập xác nhận P1 đã sửa và không thấy P1 mới. API GitHub xác nhận ruleset #25950396 active và required check được cấu hình.

## Còn lại
Sau commit tài liệu review/worklog, CI sẽ chạy lại trên head PR cuối; cần xác nhận xanh trước khi bàn giao. Chủ repo quyết định merge PR #3. Khi có máy Windows server, cài đặt theo `docs/deployment.md`; chưa thử updater/Task Scheduler/Page thật trên máy đó.
