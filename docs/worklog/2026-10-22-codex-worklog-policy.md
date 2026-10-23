# Bắt buộc ghi nhật ký cho mỗi nhiệm vụ

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi

Mỗi lần làm việc với repo phải có docs ghi lại thông tin, áp dụng cho mọi agent và không phụ thuộc plugin tùy chọn.

## Thực hiện

Tạo quy ước và mẫu nhật ký tại `docs/worklog/README.md`; ghi lại ba nhiệm vụ trước; thêm `scripts/check-worklog.mjs` để kiểm tra mục bắt buộc trước khi bàn giao. Cập nhật `AGENTS.md`, `MULTI_AGENT.md`, README, `MAP.md`, `PLAN.md` và tài liệu plugin documentation.

## Quyết định

Dùng một file cho mỗi nhiệm vụ để các agent không cùng sửa một nhật ký. Nhật ký công việc luôn bật; plugin `documentation` chỉ bổ sung tài liệu sử dụng và kiến trúc sản phẩm.

## Kiểm chứng

Đã chạy `node --check scripts/check-worklog.mjs`, kiểm tra một worklog đã hoàn tất, `node scripts/plugins.mjs check` và `git diff --check`. Lệnh kiểm tra toàn bộ đã phát hiện đúng worklog này chưa hoàn tất trước khi cập nhật trạng thái.

## Còn lại

Chưa cấu hình hook Git hoặc CI để chặn commit nếu thiếu worklog. Quy tắc hiện được các agent thực hiện qua `AGENTS.md` và kiểm tra bằng lệnh trước khi bàn giao.
