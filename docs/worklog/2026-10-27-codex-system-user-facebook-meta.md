# Hoàn tất thiết lập System User trên Meta

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Tiếp tục thao tác Meta theo xác nhận của người dùng: kết nối App CreatePost, tạo System User, gán Page Duy Quân AppleWatch và cấu hình token cục bộ. Không ghi secret vào repo hoặc nhật ký.

## Thực hiện
Đã tạo Business Portfolio, kết nối App CreatePost và Page Duy Quân AppleWatch. Đã tạo System User quyền Employee, cấp quyền nội dung và hoạt động cộng đồng trên Page, quyền thử nghiệm App, rồi tạo token 60 ngày với các quyền đọc Page, đăng nội dung và quản lý tương tác. Lưu token trong biến môi trường User trên máy này và chuyển chế độ xác thực sang `system_user`. Sửa mã hóa UTF-8 BOM của `scripts/configure-facebook-system-user.ps1` để PowerShell 5 đọc đúng; cập nhật `README.md`, `PLAN.md` và `contexte/decisions.md` theo trạng thái thực tế. Khởi động lại Flask để nạp cấu hình mới.

## Quyết định
Chỉ cấp quyền Page cần cho đăng bài và bình luận. Dùng token System User theo hạn Meta cấp, không lưu vào repo, worklog hoặc commit. Giữ khả năng dùng Page token cũ nếu chủ máy chủ động đổi chế độ xác thực.

## Kiểm chứng
Meta xác nhận System User được gán đúng App và Page. Graph API xác minh đúng tên/ID Page và trả task `CREATE_CONTENT`, `MODERATE`. `scripts/configure-facebook-system-user.ps1 -Check` xác minh Page thành công. Dashboard `/facebook` trả HTTP 200, hiển thị nguồn xác thực System User; `/facebook/identity` xác minh Page thành công. Hermes nạp lại biến môi trường User và xác minh cùng Page. `python -m unittest discover -s tests -q` đạt 79 bài kiểm tra.

## Còn lại
Chưa thử đăng một bài công khai bằng token mới, nên cần kiểm tra có kiểm soát trước khi tin tưởng lịch đăng thật. Token có hạn 60 ngày theo Meta; cần gia hạn trước khi hết hạn. Không có commit trong nhiệm vụ này.
