# Làm rõ cổng CI trước và sau merge

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích quy trình PR, CI và merge có cố định hay có thể cấu hình, đặc biệt việc CI sau merge có ngăn commit lên `main` không. Không đổi code hay quyền GitHub.

## Thực hiện
Đối chiếu workflow CI của repo với tài liệu GitHub về required status checks, workflow theo sự kiện `push` và auto-merge.

## Quyết định
Giải thích rõ pre-merge check có thể chặn merge khi được đặt là required; post-merge CI chỉ đánh giá commit đã nằm trên `main` và có thể chặn triển khai, không thể tự hoàn tác merge. Các bước có thể đổi theo chính sách nhóm.

## Kiểm chứng
Tham khảo tài liệu GitHub chính thức; không chạy test vì không sửa code.

## Còn lại
Ruleset hiện chưa bắt buộc CI; chưa có CD. Cần thiết lập riêng nếu chủ repo muốn áp dụng quy trình này.
