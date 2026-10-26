# Điều kiện thiết lập agent local đăng nhóm

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Liệt kê những gì cần để nối LLM local với ứng dụng hiện tại và thử đăng một bài vào nhóm Facebook qua trình duyệt trên máy người dùng. Chưa yêu cầu triển khai hoặc gửi bài.

## Thực hiện
Đối chiếu cấu hình 9Router/model, Playwright, lịch tự động và script chạy cục bộ. Nền tảng chọn tin/viết/ảnh/lịch đã có; chưa có nhóm đích, phiên trình duyệt Facebook riêng, adapter đăng nhóm và xác minh kết quả.

## Quyết định
Thử trước với một nhóm mà tài khoản có quyền đăng, một phiên trình duyệt đăng nhập thủ công và một bài thử. Không thu thập mật khẩu, cookie hoặc token qua chat. Dừng khi gặp xác minh đăng nhập, CAPTCHA hoặc kết quả đăng không rõ.

## Kiểm chứng
`node scripts/plugins.mjs check`: cấu hình plugin hợp lệ. Đối chiếu `requirements.txt`, `.env.example`, `app/automation.py` và script khởi động; chạy kiểm tra worklog.

## Còn lại
Cần URL nhóm, danh tính đăng (tài khoản cá nhân hay Page), quyền đăng trong nhóm, khung giờ và máy/Chrome khả dụng trước khi thử nghiệm thực tế. Chưa đăng bài.
