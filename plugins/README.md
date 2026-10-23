# Plugin quy trình của dự án

Đây là các module hướng dẫn nằm trong **repo**, dùng chung cho Codex, Antigravity và Claude Code. Chúng không phải plugin cài vào IDE hay MCP server. File `project.plugins.json` quyết định module nào đang bật; chỉ module bật mới bổ sung quy tắc làm việc cho agent.

## Quản lý

```powershell
node scripts/plugins.mjs list
node scripts/plugins.mjs enable prototype
node scripts/plugins.mjs disable prototype
node scripts/plugins.mjs check
```

Sau khi đổi cấu hình, bắt đầu phiên agent mới hoặc yêu cầu agent đọc lại `project.plugins.json`. Việc bật plugin không tự sinh code hoặc pipeline: agent triển khai theo `INSTRUCTIONS.md` của plugin khi có nhiệm vụ và thông tin dự án tương ứng.

## Bộ plugin khởi đầu

| Plugin | Khi bật |
| --- | --- |
| `prototype` | Làm và xác nhận prototype trước phần triển khai hoàn chỉnh |
| `testing` | Thiết kế và duy trì kiểm thử tự động phù hợp với stack |
| `ci-cd` | Thiết lập kiểm tra CI và luồng triển khai CD khi có đích triển khai |
| `documentation` | Duy trì tài liệu chạy, sử dụng và kiến trúc thực tế |
| `security` | Thực hiện kiểm tra bảo mật theo rủi ro của sản phẩm |
| `independent-review` | Agent khác review thay đổi code độc lập trước khi chủ repo quyết định merge |
| `codebase-graph` | Dùng source Understand Anything trong repo để tạo và làm mới graph khi cần |

Quy tắc bảo vệ secrets cơ bản trong `AGENTS.md` luôn áp dụng, kể cả khi `security` tắt.
Nhật ký công việc trong `docs/worklog/` cũng luôn bắt buộc; plugin `documentation` dành cho tài liệu sử dụng và kiến trúc sản phẩm.
Repo này đang bật `independent-review`. Xem [quy trình và mẫu review](../reviews/README.md).
`codebase-graph` cũng được bật; xem [cách dùng source vendored và trạng thái graph](../docs/understand-anything.md).

## Tạo plugin mới

Tạo `plugins/<id>/plugin.json` với `id`, `name`, `description`, và `plugins/<id>/INSTRUCTIONS.md`. Nội dung nên nêu điều kiện bắt đầu, việc agent phải làm, đầu ra có thể kiểm chứng và khi nào hoàn thành. Chạy `node scripts/plugins.mjs check` trước khi bật. Giữ plugin độc lập với công cụ agent và không tự đặt giả định về stack.
