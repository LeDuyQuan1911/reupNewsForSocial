# Thiết lập review code độc lập giữa các agent

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi

Tạo cách để một agent viết code và agent khác review dễ dàng, giảm thiên vị trong nhận xét.

## Thực hiện

Tạo plugin `plugins/independent-review/` và bật trong `project.plugins.json`. Thêm `reviews/README.md`, mẫu yêu cầu và báo cáo, cùng `scripts/review-brief.mjs` để tạo brief chỉ từ base/head và danh sách file thay đổi. Cập nhật `AGENTS.md`, `MULTI_AGENT.md`, README, `MAP.md`, `PLAN.md` và danh mục plugin.

## Quyết định

Lượt review đầu dùng ngữ cảnh riêng, yêu cầu trung tính và bằng chứng từ diff/code; lời giải thích của tác giả được xem ở lượt đối chiếu sau. Reviewer ghi phát hiện có thể kiểm chứng và không quyết định merge. Quy trình này giảm ảnh hưởng của thiên vị, không bảo đảm ẩn danh hoặc loại bỏ mọi thiên vị.

## Kiểm chứng

Chạy `node --check scripts/review-brief.mjs`, `node scripts/plugins.mjs check` (6 plugin, 1 đang bật), thử `--dry-run` với hai ref hợp lệ và xác nhận lệnh không tạo brief thật khi không có file thay đổi. Chạy `git diff --check`.

## Còn lại

Chưa có commit thay đổi code để chạy một phiên review thực tế; các thay đổi hiện tại vẫn chưa commit. Quy trình review là quy tắc repo, chưa được GitHub tự động bắt buộc.
