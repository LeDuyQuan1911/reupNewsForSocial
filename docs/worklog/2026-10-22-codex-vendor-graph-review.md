# Review vendor graph

- Ngày: 2026-10-22
- Agent: Codex reviewer
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Review độc lập thay đổi vendor Understand Anything, đánh dấu graph cũ sau commit và làm mới khi dùng; chỉ sửa report và worklog reviewer.

## Thực hiện
Đọc SPEC, plugin, script, hook, tài liệu và phần source vendored liên quan. Ghi báo cáo tại `reviews/reports/vendor-understand-anything.md`; phát hiện P2 về đường dẫn graph legacy. Sau bản sửa, đối chiếu hai script và cập nhật report.

## Quyết định
Đối chiếu script mới với hàm `resolveUaDirName` và hướng dẫn skill vendored; giữ lượt đầu độc lập, không đọc worklog tác giả trước report.

## Kiểm chứng
`node scripts/graph-status.mjs` trả `MISSING` khi chưa có graph; `node --check` hai script, `node scripts/plugins.mjs check`, `git diff --check` đạt. `git check-ignore -v` xác nhận các đường dẫn graph và build được ignore. Probe Git repo tạm ban đầu thất bại do sandbox; sau sửa, fixture legacy trong checkout hiện tại cho `CURRENT`, marker ghi vào đúng legacy với head khớp. Fixture đã xóa.

## Còn lại
Phát hiện P2 đã được xác nhận sửa trong working tree. Chưa chạy setup, hook qua commit thật hoặc refresh LLM; file mới vẫn chưa commit nên cần đưa bản sửa vào commit dự kiến tích hợp.
