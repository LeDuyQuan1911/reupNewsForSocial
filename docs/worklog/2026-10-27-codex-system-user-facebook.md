# Chuyển kết nối Facebook Page sang System User

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: bị chặn

## Yêu cầu và phạm vi
Người dùng muốn chuyển kết nối đăng Facebook Page hiện tại sang Meta System User để chạy tự động bền hơn. Không đưa token vào repo, log hoặc chat.

## Thực hiện
Đã chuẩn bị chế độ System User cho lệnh đăng Page, kiểm tra Page, dashboard và Hermes; thêm script cấu hình token vào biến môi trường User, không ghi token vào repo. Trên Meta đã tạo Business Portfolio `Lê Duy Quân` (ID `1084925844441338`) và gán đúng Page Duy Quân AppleWatch. App CreatePost, System User và token chưa được gán/tạo.

## Quyết định
Dùng System User token để lấy Page token tương ứng với Page ID khi gọi Graph API; không tự rơi về token Page cũ nếu System User lỗi. Chỉ gán Page mà người dùng chỉ định; không mời thêm người khác vào Portfolio.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 79 bài kiểm tra đạt. PowerShell parser cho hai script cấu hình đạt. `git diff --check` đạt. Đã đối chiếu Hermes runner cài trên máy với bản repo. Chưa kiểm chứng token System User hay thao tác đăng Page thực tế.

## Còn lại
Công cụ computer-use dừng do không xác định chắc URL trình duyệt trên Windows; phải dừng thao tác Meta trong lượt này. Cần kết nối App CreatePost với Portfolio, tạo System User, gán Page và App, tạo token theo quyền cần thiết, nhập qua `scripts/configure-facebook-system-user.ps1`, kiểm tra Page và thử đăng có kiểm soát. Email liên hệ trong Portfolio đang chờ xác nhận. Không commit/push/merge trong nhiệm vụ này.
