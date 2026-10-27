# Ưu tiên nhiều ảnh cho bài đăng

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cho bước chuẩn bị bài tự động ưu tiên nhiều ảnh thực tế liên quan thay vì chỉ lấy ảnh đầu tiên, nhưng vẫn giữ giới hạn và kiểm duyệt trước đăng.

## Thực hiện
`app/media.py`: khi tạo bản nháp, thử lưu tối đa ba ảnh nguồn khác nhau, loại URL và dữ liệu ảnh trùng; với repo ít ảnh README, thử ảnh chụp repo làm tư liệu bổ sung. Ảnh thẻ tiêu đề tạm bị loại khỏi danh sách gửi thật khi có ảnh dùng được. `app/automation.py`: kiểm duyệt từng ảnh; loại ảnh nguồn không đạt nếu còn ảnh hợp lệ, giữ bài bị chặn khi không còn ảnh đạt. `app/web.py`, `app/templates/post.html`: báo số ảnh chuẩn bị và nêu khả năng ưu tiên nhiều ảnh. Cập nhật `README.md`, `SPEC.md`, `PLAN.md`, `contexte/decisions.md` và kiểm tra trong `tests/test_app.py`, `tests/test_automation.py`. Khởi động lại server dashboard để nạp mã mới.

## Quyết định
Ưu tiên tối đa ba ảnh thật khác nhau cho bản nháp mới, không thêm ảnh trùng hoặc ảnh AI chỉ để đạt số lượng. Nếu nguồn chỉ cung cấp một ảnh hợp lệ thì vẫn dùng một ảnh; người dùng có thể thêm ảnh trước khi lên lịch. Giữ giới hạn tối đa 10 ảnh và kiểm duyệt lại khi đăng.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 86 bài kiểm tra đạt. `python -m compileall -q app` và `git diff --check`: đạt. Sau restart, `/posts/25` trả HTTP 200 và hiển thị hướng dẫn ưu tiên nhiều ảnh.

## Còn lại
Chưa thử trên bài báo hoặc repo thật trong nhiệm vụ này; số ảnh thực tế phụ thuộc ảnh đủ lớn, truy cập được và qua model kiểm duyệt. Bài đã có lịch hoặc đã đăng không tự thay ảnh. Không commit hoặc push.
