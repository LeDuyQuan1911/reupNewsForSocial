# Tạo bản nháp từ tin mới

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn xem các bản nháp viết từ tin mới trong thời gian thực. Chỉ tạo bản nháp có ảnh trong dashboard, không lên lịch hoặc đăng Facebook.

## Thực hiện
Quét lại bảy nguồn đang bật: không có bài mới thêm trong lần quét. Đối chiếu các bài gần nhất với nguồn chính thức. Tạo ba bản nháp có ảnh nguồn trong SQLite cục bộ: post #20 (NVIDIA Microduck, nguồn 23/10), #21 (AWS Multi-Turn RL, nguồn 23/10), #22 (Microsoft Research Flint-interactive, nguồn 22/10). Viết qua model đã cấu hình, sửa các chỗ diễn đạt có thể gây hiểu lầm và link nguồn lặp, rồi lưu ở trạng thái `draft`. Mở dashboard Flask chế độ xem trước tại localhost:5000; không chạy tiến trình tự động đăng.

## Quyết định
Ưu tiên nguồn chính thức và bài gần nhất, không lặp bản nháp hoặc bài đã đăng. Vì nguồn chưa có bài phát hành hôm nay, nêu rõ ngày nguồn thay vì gọi là tin mới trong ngày. Dùng model đã cấu hình, giữ thông tin đăng nhập ngoài repo và chỉ tạo bản nháp để người dùng duyệt.

## Kiểm chứng
Trang `/posts/20`, `/posts/21`, `/posts/22` đều trả HTTP 200. Kiểm tra SQLite xác nhận cả ba ở trạng thái `draft`, không có lịch hoặc thời điểm đăng; mỗi bài có một ảnh JPEG nguồn, hashtag và một dòng nguồn. Đã xem trực quan cả ba ảnh. `data/` được Git bỏ qua. Script tạm dùng để tạo bản nháp đã xóa.

## Còn lại
Chưa kiểm duyệt bằng model nhìn ảnh hoặc gửi Facebook vì người dùng muốn xem bản nháp. Nguồn gần nhất trong lựa chọn là 22–23/10, không có tin mới thêm khi quét ngày 26/10. Người dùng có thể chỉnh nội dung/ảnh trên dashboard trước khi quyết định lên lịch hoặc đăng.
