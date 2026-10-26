# Hướng dẫn kết nối Facebook và đăng nhóm

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích cách kết nối Facebook để ứng dụng đăng bài, và đánh giá khả năng đăng vào nhóm dựa trên code hiện tại cùng tài liệu Meta hiện hành. Không đổi cấu hình hoặc gửi bài thật.

## Thực hiện
Đọc `app/facebook.py`, `app/automation.py`, `.env.example`, trang Tài khoản và tài liệu repo. Xác nhận adapter chỉ gọi Graph API cho Page (`/photos`, `/feed`), nhận Page ID/token/version từ biến môi trường. Kiểm tra tên biến cấu hình trong User environment (chỉ giá trị đúng/sai, không đọc nội dung): ba biến Facebook hiện chưa đặt. Tra cứu bộ sưu tập Facebook API do Meta xuất bản về cách lấy Page access token từ `/me/accounts`, trợ giúp Facebook về đăng/chia sẻ trong nhóm, và thông báo thay đổi Groups API v19.0.

## Quyết định
Đề xuất kết nối Page qua ứng dụng Meta và Page access token; không giả định token Page có quyền đăng nhóm. Với nhóm, ưu tiên chia sẻ thủ công từ Page hoặc quy trình chuẩn bị bài để người dùng đăng trong giao diện Facebook; đăng tự động bằng phiên trình duyệt cần kiểm chứng riêng và không bảo đảm ổn định.

## Kiểm chứng
Đối chiếu endpoint, biến môi trường và trạng thái cấu hình cục bộ; không gửi thử bài hoặc in token. `node scripts/check-worklog.mjs` trước bàn giao.

## Còn lại
Cần chủ Page tạo/cấp quyền ứng dụng và Page token trước khi thử gửi bài. Chưa kiểm chứng quyền thực tế hoặc một lần đăng Page thành công. Tài liệu Meta Developer trực tiếp trả 429 trong lượt tra cứu nên dựa thêm vào bộ sưu tập API do Meta xuất bản và liên kết thông báo v19.0.
