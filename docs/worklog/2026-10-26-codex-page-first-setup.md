# Ưu tiên kết nối Facebook Page

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Tạm để đăng nhóm, chuẩn bị luồng đăng Facebook Page trước. Người dùng có Page nhưng chưa có Page access token.

## Thực hiện
Đối chiếu adapter Page và tài liệu Pages API do Meta công bố; người dùng xác nhận có Page nhưng chưa tạo Meta App/token. Thêm `scripts/configure-facebook-page.ps1`: nhập token ẩn, kiểm tra `GET /<page-id>?fields=id,name` rồi mới lưu ID/version/token vào biến môi trường User. Đặt hướng dẫn Page ở đầu `app/templates/facebook.html`, thu gọn phần nhóm; liên kết từ `app/templates/account.html`. Cập nhật CSS, README, MAP, SPEC, PLAN, quyết định và test. Khởi động lại dashboard để giao diện hiện trên localhost.

## Quyết định
Page là ưu tiên hiện tại; nhóm vẫn lưu được nhưng mặc định thu gọn và chưa gửi. Kiểm tra đọc chỉ xác nhận token truy cập đúng Page, không suy ra quyền đăng; script không tự khởi động lại dịch vụ hoặc tự đăng bài khi lưu token. Giữ token ngoài repo/chat.

## Kiểm chứng
Parser PowerShell không lỗi; `-Check` khi chưa có token dừng với thông báo phù hợp. `python -m unittest discover -s tests -v`: 42 test đạt; test nhóm liên quan đạt sau khi thu gọn UI. `/facebook` trả HTTP 200. Chụp desktop và điện thoại, không tràn ngang ở 390 px; phần nhóm thu gọn mặc định.

## Còn lại
Người dùng cần tự tạo Meta App và cấp quyền cho Page, lấy Page access token. Chưa thể kiểm tra token hoặc đăng thử vì token chưa có. Sau khi có token, chạy script cục bộ, xem bài chờ, khởi động lại dashboard và thử một bài trước khi để lịch tự chạy.
