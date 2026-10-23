# Thiết lập nền tảng repo cho coding agent

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: hoàn tất
- Ghi chú: ghi lại sau khi hoàn thành, theo yêu cầu bổ sung nhật ký.

## Yêu cầu và phạm vi

Đọc bài viết về harness ba tầng và thiết lập repo để agent có ngữ cảnh trước khi vibe code. Repo ban đầu chỉ có README và Git.

## Thực hiện

Tạo `AGENTS.md`, `CLAUDE.md`, `MAP.md`, `SPEC.md`, `PLAN.md`, `contexte/decisions.md`, `livrables/README.md`, `.gitignore` và cập nhật README. Không tạo source ứng dụng khi chưa có đặc tả sản phẩm.

## Quyết định

Dùng tài liệu repo làm nền tảng; chưa chọn stack, MCP hoặc ứng dụng khi thiếu yêu cầu.

## Kiểm chứng

Đã xem trạng thái Git, chạy `git diff --check` và kiểm tra `.env` được `.gitignore` loại trừ.

## Còn lại

Cần người dùng trả lời các câu hỏi trong `SPEC.md` trước khi xây ứng dụng.
