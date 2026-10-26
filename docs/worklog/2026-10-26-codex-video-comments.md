# Video trong bình luận Facebook Page

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Với bài báo có video phù hợp, thêm dòng báo video nằm trong bình luận và tự đăng liên kết video ở bình luận của bài Facebook Page sau khi bài đăng thành công.

## Thực hiện
Đã thêm `app/video.py` để đọc metadata video, thẻ video, YouTube/Vimeo nhúng và liên kết video rõ ràng từ trang bài báo công khai; model 9Router chọn một video liên quan khi có đủ metadata. Luồng tự động lưu URL video vào bản nháp và thêm dòng chỉ dẫn; trang biên tập cho tìm hoặc dán/sửa URL thủ công. SQLite có thêm URL, trạng thái, ID và lỗi bình luận, gồm migration cho dữ liệu hiện có. Adapter Facebook bình luận liên kết sau khi bài đã được xác nhận đăng thành công. Hàng đợi tách lỗi bình luận, hiển thị trong Cần xử lý và có bước đối chiếu thủ công trước khi gửi lại. Cập nhật template, kiểm thử, README, SPEC, PLAN, MAP và quyết định dự án. Script khởi động nạp thêm biến model ảnh đã có từ máy người dùng khi tải lại dashboard.

## Quyết định
Chỉ dùng video gắn trực tiếp hoặc liên kết video rõ ràng trong trang nguồn; khi không chắc tính liên quan, bỏ qua. Không tự thử lại bình luận sau timeout vì có thể Facebook đã nhận; người dùng phải kiểm tra Page và xác nhận đã có hoặc vắng trước khi gửi. Không gửi lại cả bài chỉ vì bình luận lỗi.

## Kiểm chứng
`python -m py_compile app/video.py app/database.py app/facebook.py app/queue.py app/automation.py app/web.py`: đạt. `python -m unittest discover -s tests -p 'test_*.py'`: 57 kiểm thử đạt, gồm chọn video, tạo bình luận sau đăng, không retry sau timeout và đối chiếu thủ công. Flask test client mở `/posts/20`: HTTP 200, thấy phần video. Đã khởi động lại dashboard khi không có bài ở trạng thái `publishing`; GET thật `http://127.0.0.1:5000/posts/20` trả HTTP 200 và có phần video. Đã kiểm tra bài nguồn của bản nháp #20 qua bộ phát hiện mới: không thấy URL video phù hợp, nên không thay nội dung. `git diff --check` với file nhiệm vụ: đạt.

## Còn lại
Chưa gửi bình luận thật lên Facebook Page; Page token cần được kiểm chứng có quyền bình luận trên một bài thật. Model mới chỉ đánh giá tiêu đề/metadata của video, chưa xem nội dung hình/âm thanh; player riêng không có thẻ/link rõ ràng cần dán URL thủ công. Bản nháp #20 hiện chưa có video được chọn và không bị thêm lời hứa video.
