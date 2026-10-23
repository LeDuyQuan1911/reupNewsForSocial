# Thử viết lại bài và lên lịch không đăng

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thử dùng AI viết lại nội dung, tạo ảnh minh họa cho một bài báo đã thu thập, lên lịch thử nghiệm và bảo đảm lịch này không được đăng lên Facebook.

## Thực hiện
Đối chiếu bài Oracle trên trang nguồn. Dùng 9Router tạo bản nháp tiếng Việt, sửa một tên sản phẩm sai trong đầu ra AI, rồi lưu nội dung cho bài đăng #6. Dùng imagegen tạo ảnh minh họa khái niệm, chuyển sang JPEG và gắn vào bài #6. Đặt lịch thử nghiệm 10:00 ngày 24/10/2026 (Asia/Bangkok). Thêm cờ `test_only` vào `app/database.py`; hàng đợi và thao tác đăng ngay bỏ qua bài thử. Cập nhật `app/web.py`, `app/queue.py`, giao diện biên tập và workflow, `SPEC.md`, `PLAN.md`, `contexte/decisions.md`, và kiểm thử.

## Quyết định
Lịch thử nghiệm được lưu như lịch hẹn để xem trước nhưng không chiếm khung giờ tự động và không thể gửi Facebook. Ảnh AI được ghi rõ là ảnh minh họa; không dùng để thể hiện một sự kiện có thật.

## Kiểm chứng
`python -m unittest discover -s tests`: 25 bài kiểm thử đạt. `git diff --check`: đạt. Kiểm tra trực tiếp bài #6 với giờ quá hạn giả lập: hàng đợi không nhận, thao tác đăng ngay không claim. Server localhost trả HTTP 200 cho trang bài, ảnh JPEG và workflow; giao diện có nhãn lịch thử nghiệm.

## Còn lại
Chưa kết nối Facebook Page nên chưa kiểm tra đăng thật; lịch thử nghiệm này vẫn bị chặn khi sau này thêm kết nối. Muốn đăng bài này cần hủy lịch thử và đặt lịch thật.
