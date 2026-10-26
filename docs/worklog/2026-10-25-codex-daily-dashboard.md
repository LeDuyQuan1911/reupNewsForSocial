# Dashboard theo ngày

- Ngày: 2026-10-25
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn trang Tổng quan thành dashboard có thống kê theo từng ngày và số bài hệ thống chạy mỗi ngày, bỏ khối “Dịch vụ của bạn”.

## Thực hiện
Thêm truy vấn tổng hợp 7/30 ngày trong `app/database.py`, tính theo ngày Bangkok và điền ngày không có hoạt động bằng số 0. Đổi route và template Tổng quan để hiển thị số liệu hôm nay, biểu đồ 7 ngày, dòng thống kê từng ngày và trạng thái vận hành ngắn. Bỏ toàn bộ khối “Dịch vụ của bạn”. Thêm CSS responsive, test múi giờ/những ngày trống, cập nhật README, MAP, SPEC, PLAN và quyết định kỹ thuật.

## Quyết định
Phân biệt “bài viết tạo” (mọi bản nháp mới), “tự động đạt” (job hiện ready/scheduled, gắn vào ngày bắt đầu) và “đã đăng” (bài có trạng thái published). Không coi bài đã chuẩn bị là đã gửi Facebook.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 31/31 test đạt. Dashboard localhost trả HTTP 200 ở chế độ 7 và 30 ngày; Playwright xác nhận lần lượt 7/30 dòng, không tràn ngang ở 1440px và 390px. Server localhost:5000 đã tải lại bản mới.

## Còn lại
Job tự động được tính theo ngày bắt đầu và trạng thái hiện tại nên số liệu ngày cũ có thể đổi nếu job đổi trạng thái. Diff giao diện chưa qua review độc lập trước khi merge vào `main`.
