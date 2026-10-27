# Làm rõ yêu cầu Meta App khi lấy Page token

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Kiểm tra nhận xét rằng lấy Page token có thể không cần tạo Meta App mới; sửa hướng dẫn gây hiểu nhầm trong dashboard và README.

## Thực hiện
Đối chiếu `app/facebook.py` với bộ ví dụ Pages API của Meta: ứng dụng không dùng App ID/App Secret, chỉ dùng Page ID, Page token và phiên bản Graph API. Sửa `app/templates/facebook.html`, README, SPEC và quyết định để nói rõ token hợp lệ từ App/tích hợp phù hợp được chấp nhận, tạo App mới chỉ là một cách lấy token. Khởi động lại dashboard.

## Quyết định
Không khẳng định có thể tự lấy Page token bằng Graph API Explorer mà không chọn App; tài liệu chính thức dùng App cho luồng Explorer. Phân biệt yêu cầu của ứng dụng (token) với một cách cấp token (tạo App mới).

## Kiểm chứng
Test route Facebook liên quan đạt; `git diff --check` cho các file sửa không báo lỗi; `/facebook` trả HTTP 200 và hiển thị copy đã sửa. Script cấu hình Page không đổi.

## Còn lại
Người dùng vẫn cần Page token có quyền đăng và thử một bài thật; hiện chưa có token nên chưa thể xác nhận quyền gửi. Không có việc sửa code còn lại trong yêu cầu này.
