# Tự chuẩn bị nhiều ảnh cho bài đăng

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Hệ thống tự bổ sung ảnh để bài đăng có thể có nhiều ảnh mà người dùng không phải tự tải ảnh lên. Ưu tiên ảnh thật, dùng 9Router khi nguồn thiếu ảnh, giữ kiểm duyệt và chống trùng.

## Thực hiện
`app/media.py`: sau khi ưu tiên ảnh nguồn và ảnh chụp repo, tự gọi model ảnh 9Router tạo ảnh bổ sung khi còn ít hơn hai ảnh thật; nếu nguồn không có ảnh, thử tạo hai ảnh AI khác nhau, bỏ ảnh trùng dữ liệu. Thêm `ensure_multiple_images` để bản nháp cũ còn một ảnh được thử bổ sung khi chuẩn bị đăng. `app/llm.py`: tạo prompt ảnh thứ hai với bố cục minh họa riêng, hạn chế giả giao diện/logo/thương hiệu, và đọc được JSON kiểm duyệt có hàng rào markdown. `app/web.py`: dùng bước bổ sung ảnh khi lên lịch hoặc đăng ngay. Cập nhật `README.md`, `SPEC.md`, `PLAN.md`, `contexte/decisions.md`, `app/templates/post.html` và kiểm tra trong `tests/test_app.py`.

## Quyết định
Ảnh thật vẫn được ưu tiên. Chỉ thử sinh ảnh khi thiếu ảnh thứ hai; không bắt người dùng tải ảnh. Nếu 9Router lỗi, trả ảnh trùng hoặc model nhìn ảnh từ chối ảnh thứ hai, bài vẫn có thể giữ một ảnh hợp lệ thay vì chặn vô hạn. Không tự đổi ảnh của bài đã lên lịch hoặc đã đăng.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 90 bài kiểm tra đạt. `python -m compileall -q app` và `git diff --check`: đạt. Kiểm tra model ảnh hiện có trong 9Router; dùng model ảnh thật để tự thay ảnh thẻ tạm của bản nháp #25 bằng hai ảnh AI, quan sát hình, thay ảnh bổ sung lặp bố cục bằng hình minh họa khác và dùng model nhìn ảnh xác nhận phù hợp. Sau restart, `/posts/25` trả HTTP 200 và hiển thị 2/10 ảnh.

## Còn lại
Không có thử đăng thật lên Facebook trong nhiệm vụ này. Chất lượng/số lượng ảnh vẫn phụ thuộc tư liệu nguồn và phản hồi model ảnh/vision của 9Router; mỗi ảnh AI bổ sung làm tăng thời gian và chi phí model. Mã nguồn chưa được commit hoặc push.
