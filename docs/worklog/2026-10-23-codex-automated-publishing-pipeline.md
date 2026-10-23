# Tự động hóa luồng tìm và đăng bài

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn hệ thống tự quét nguồn, tạo bài và đăng theo lịch mà không cần bấm từng bước trên dashboard.

## Thực hiện
Thêm `app/discovery.py` để dùng chung quét nguồn thủ công/tự động; `app/automation.py` và bảng trạng thái/công việc trong `app/database.py` để quét mỗi giờ, chuẩn bị tối đa sáu bài đạt từ tin trong 48 giờ theo ngày Bangkok, tạo ảnh và nội dung bằng 9Router, kiểm duyệt ảnh/nội dung, chống tiêu đề tương tự, thử lại lỗi chuẩn bị tối đa ba lần và chỉ xếp lịch khi đủ cấu hình Facebook Page. Khi bài bị chặn hoặc lỗi hết lượt thử, có thể chọn bài khác để bù khung còn trống. Cập nhật `run.py`, trang tài khoản, `.env.example`, README/MAP/SPEC/PLAN và quyết định kỹ thuật. Thêm `scripts/start-local-services.ps1` và đăng ký Windows Scheduled Task `reupNewsForSocial-local` khi người dùng đăng nhập. Đặt `REUP_AUTO_ENABLED=1` trong biến môi trường người dùng, khởi động lại dashboard và cho phép chọn tin đã lưu nhưng vẫn còn mới. Không thay đổi các bản nháp thủ công.

## Quyết định
Chọn sáu khung giờ 07, 10, 13, 16, 19, 22 (Bangkok), tối đa sáu tin/ngày, quét mỗi giờ. Bài đã lưu trong 48 giờ và chưa có bản nháp cũng được xét ở lượt đầu. Giữ chốt kiểm duyệt ảnh/nội dung và chống đăng trùng; bài bị chặn không tự retry. Không ghi secrets vào repo hoặc worklog.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 24 test đạt, gồm giới hạn sáu bài đạt, bài bị chặn được thay thế, lịch khi có Page và retry lỗi tạm thời. `git diff --check` không báo lỗi định dạng. Script startup chạy thành công; Windows Scheduled Task chạy thử với mã kết quả 0. Dashboard `127.0.0.1:5000` và 9Router `127.0.0.1:20128` đang chạy. Lượt thật quét nguồn không có lỗi; sáu bài được nhận xử lý, năm bản nháp đạt và một bài đã thử lại hai lần vẫn lỗi tại thời điểm kiểm tra. Chưa gửi bài lên Facebook.

## Còn lại
Cần Page ID, Page access token và Graph API version để tự xếp lịch/gửi thật. Bài lỗi còn một lần thử tự động; nguồn hiện tại không bảo đảm đủ sáu tin đạt yêu cầu mỗi ngày. Quy trình chỉ hoạt động khi máy bật và người dùng đăng nhập Windows; việc đăng Page thật chưa thể kiểm thử. Các kênh trang cá nhân, nhóm và LinkedIn chưa tích hợp.
