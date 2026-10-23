# Nhiều ảnh cho một bài đăng

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cho phép một bài đăng giữ nhiều ảnh, tối thiểu một ảnh khi lên lịch hoặc đăng; ảnh chụp repo GitHub là một loại ảnh hợp lệ.

## Thực hiện
Thêm bảng `post_images` và chuyển ảnh đơn cũ trong `app/database.py`. Cập nhật `app/media.py`, `app/web.py` và `app/templates/post.html` để xem nhiều ảnh, thêm ảnh từ nguồn hoặc tải lên, bỏ ảnh khi còn ít nhất một, và chụp thêm repo GitHub. `app/queue.py` và `app/automation.py` kiểm duyệt từng ảnh. `app/facebook.py` giữ cách gửi ảnh đơn và hỗ trợ nhiều ảnh bằng tải ảnh chưa xuất bản rồi gắn vào một bài Page. Cập nhật CSS, README/MAP/SPEC/PLAN và quyết định. Thêm ảnh thứ hai vào bài thử #6, giữ nguyên lịch thử nghiệm.

## Quyết định
Giới hạn ở 10 ảnh/bài theo phạm vi ứng dụng. Không cho lên lịch hoặc nhận đăng bài không có ảnh; khi xóa ảnh trên giao diện phải còn ít nhất một. Giữ cột ảnh cũ làm ảnh đầu để không làm hỏng dữ liệu và route cũ.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 30 kiểm thử đạt, gồm chuyển dữ liệu cũ, tải lên/xóa ảnh, chụp thêm repo, kiểm duyệt ảnh thứ hai và tạo payload nhiều ảnh Facebook. `git diff --check`: đạt. Kiểm tra server localhost: bài #6 hiển thị 2 ảnh (cả hai trả HTTP 200), lịch thử nghiệm không được hàng đợi nhận; 13 bài có ảnh cũ đều có bản ghi trong bảng mới.

## Còn lại
Chưa kiểm thử lời gọi nhiều ảnh với Facebook Page thật vì chưa có Page ID/token. File ảnh được bỏ khỏi bài vẫn giữ trên đĩa để tránh xóa dữ liệu cũ ngoài ý muốn; có thể bổ sung dọn file có kiểm soát sau.
