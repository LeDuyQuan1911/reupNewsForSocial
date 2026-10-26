# Tổng quan chỉ hiển thị thông tin của người dùng

- Ngày: 2026-10-25
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn trang Tổng quan chỉ hiển thị thông tin và trạng thái hệ thống của mình, không liệt kê bài báo hoặc bài đăng.

## Thực hiện
Đổi route `/` để chỉ lấy số liệu tổng hợp, trạng thái tự động hóa và cờ cấu hình kết nối; bỏ truy vấn sáu bài báo/bài đăng gần đây. Thay hai danh sách trên `dashboard.html` bằng thẻ số liệu và trạng thái vận hành/kết nối, không hiển thị tiêu đề từng bài. Bổ sung CSS responsive, cập nhật README, SPEC, PLAN và test hồi quy.

## Quyết định
Không thêm hồ sơ cá nhân hoặc dữ liệu nhận dạng vì ứng dụng chưa có tài khoản người dùng. "Thông tin của tôi" được thể hiện bằng dữ liệu và cấu hình hệ thống trên máy này. Giữ tiêu đề trang ở dạng chỉ đọc bằng trình đọc màn hình, tránh khối heading lớn mà người dùng đã yêu cầu bỏ trước đây.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 30/30 test đạt. Flask test client xác nhận `/` trả 200 và không có hai danh sách cũ. Server localhost:5000 được tải lại; GET `/` trả 200. Chụp desktop 1440px và mobile 390px bằng Playwright; không tràn ngang.

## Còn lại
Trạng thái kết nối chỉ dựa vào biến cấu hình, chưa xác thực dịch vụ thực tế. Diff giao diện chưa qua review độc lập trước khi merge vào `main`.
