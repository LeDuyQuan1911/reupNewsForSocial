# Kiểm tra yêu cầu API của Understand Anything

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Trả lời liệu source Understand Anything đã vendored trong repo có cần API hoặc API key để dùng hay không.

## Thực hiện
Đọc skill `understand`, mã nguồn core có dùng biến môi trường và hướng dẫn tích hợp trong repo. Không sửa code.

## Quyết định
Không có.

## Kiểm chứng
Skill gọi agent/LLM để phân tích source và ghi graph, không thấy yêu cầu một API key riêng cho Understand Anything trong luồng codebase. Tìm trong core thấy `FIGMA_TOKEN` chỉ ở nhánh đọc Figma API. Hook sau commit và lệnh kiểm tra trạng thái graph chạy cục bộ bằng Node/Git.

## Còn lại
Runtime vendored trong checkout này chưa build xong do thiếu package trong cache offline; khi phân tích thật vẫn cần quyền dùng LLM của Codex/Claude/Antigravity và có thể phát sinh chi phí theo nền tảng đó.
