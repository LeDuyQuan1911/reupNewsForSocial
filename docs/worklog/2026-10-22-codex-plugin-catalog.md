# Tạo bộ plugin quy trình

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: hoàn tất
- Ghi chú: ghi lại sau khi hoàn thành, theo yêu cầu bổ sung nhật ký.

## Yêu cầu và phạm vi

Cho phép gắn hoặc tháo các module như prototype và CI/CD theo nhu cầu của từng dự án.

## Thực hiện

Tạo `project.plugins.json`, `scripts/plugins.mjs`, danh mục trong `plugins/` gồm prototype, testing, ci-cd, documentation và security. Cập nhật quy tắc agent để chỉ áp dụng plugin đang bật.

## Quyết định

Plugin là module quy trình trong repo, không phải plugin cài vào IDE; mặc định tất cả tắt. Việc bật plugin không tự tạo code khi chưa có nhiệm vụ và thông tin sản phẩm.

## Kiểm chứng

Chạy kiểm tra cú pháp Node, `list`, `check`, bật rồi tắt prototype và thử id không tồn tại. Cấu hình cuối cùng trở lại danh sách rỗng.

## Còn lại

Cần chọn plugin muốn bật cho dự án thực tế và hoàn thiện `SPEC.md`.
