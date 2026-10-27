# Trang quản lý nhóm Facebook đích

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thêm trang riêng trong dashboard để chọn nhóm Facebook dự kiến đăng, lưu tên/URL và trạng thái bật/tắt. Chưa triển khai đăng nhóm thật.

## Thực hiện
Thêm bảng `facebook_groups` trong `app/database.py`; kiểm tra URL trong `app/facebook_groups.py`; route xem/thêm/bật-tắt/xóa tại `app/web.py`; mục Facebook trong điều hướng và trang `app/templates/facebook.html` với CSS riêng. Cập nhật README, MAP, SPEC, PLAN, quyết định và test. Khởi động lại dashboard trên cổng 5000. Chỉ lưu nhóm vào SQLite; không nối vào lịch hoặc gửi Facebook.

## Quyết định
Trang thể hiện rõ hai trạng thái khác nhau: nhóm đã chọn chỉ là đích dự kiến, còn Page có cấu hình theo biến môi trường. Chỉ chấp nhận URL HTTPS thuộc facebook.com trỏ trực tiếp tới `/groups/<id-hoặc-slug>`; không tải URL khi lưu. Cho tạm dừng và xóa nhóm để sửa danh sách mà không ảnh hưởng bài đăng.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 42 test đạt, gồm CSRF, URL giả mạo, URL bài trong nhóm, chống trùng, tạm dừng và xóa. `/facebook` trả HTTP 200 sau khi khởi động lại. Chụp trang ở 1440 px và 390 px, không tràn ngang trên điện thoại. Kiểm tra diff và worklog trước bàn giao.

## Còn lại
Chưa có adapter đăng nhóm hoặc liên kết nhóm với bài/lịch; cần quyết định danh tính đăng, cơ chế thao tác và thử với nhóm người dùng có quyền. Chưa kiểm tra Page token thật. Không có bước khác của trang quản lý nhóm.
