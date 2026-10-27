# Chẩn đoán token Facebook Page

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Xác định lý do Meta từ chối token Page hiện cấu hình, không in hoặc lưu token.

## Thực hiện
Gọi Meta Graph API chỉ đọc cho Page hiện cấu hình và chỉ trích mã lỗi/loại lỗi/thời gian; không in token. Meta trả `OAuthException` code 190, subcode 463 và thông báo phiên hết hạn 26/10/2026 lúc 06:00 PDT (20:00 Bangkok). Cập nhật `app/facebook.py` để nhận ra lỗi này và hiện cảnh báo token hết hạn trên trang Facebook; thêm test tương ứng và mở lại server.

## Quyết định
Phân biệt lỗi hết hạn từ mã Graph API có cấu trúc; không trả thông báo thô của Meta vì có thể chứa dữ liệu không cần đưa vào giao diện.

## Kiểm chứng
Yêu cầu Graph API thực tế trả 190/463; GET `/facebook/identity` sau sửa trả cảnh báo hết hạn, không chứa token. `python -m unittest discover -s tests -q`: 75 test đạt. `git diff --check`: đạt.

## Còn lại
Token đã hết hạn; cần lấy Page access token mới và nhập bằng `scripts/configure-facebook-page.ps1`, rồi khởi động lại dashboard. Chưa commit hoặc push vì không được yêu cầu.
