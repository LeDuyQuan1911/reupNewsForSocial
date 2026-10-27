# Nhiều ảnh, icon và bình luận cho bài đăng

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cho bài đăng có nhiều ảnh, nhiều icon phù hợp và ít nhất một bình luận sau khi đăng Facebook Page.

## Thực hiện
`app/templates/post.html` và `app/web.py`: cho chọn nhiều ảnh trong một lần tải (vẫn tối đa 10), thêm ô sửa bình luận đầu tiên và thao tác đối chiếu nếu kết quả gửi chưa rõ. `app/hermes_writer.py`, `app/llm.py`, `docs/editorial-brief.md`: Hermes thử viết bình luận riêng theo dữ kiện bài và được gợi dùng nhiều icon có ý nghĩa trong bài, không áp số lượng cố định. `app/database.py`, `app/queue.py`, `app/facebook.py`, `app/automation.py`: lưu nội dung/trạng thái bình luận, kiểm duyệt cùng bài và ảnh, gửi sau khi Meta trả ID bài đăng, không gửi lại mù. Cập nhật `README.md`, `SPEC.md`, `PLAN.md`, `contexte/decisions.md` theo tính năng thực tế. Thêm kiểm tra vào `tests/test_app.py`, `tests/test_hermes_writer.py`. Khởi động lại server Flask để nạp mã mới.

## Quyết định
Giữ cơ chế 1–10 ảnh vốn có và bổ sung chọn nhiều file cùng lúc. Bình luận đầu tiên luôn có nội dung nguồn dự phòng để bài tự động không bị bỏ trống khi Hermes lỗi; người dùng có thể sửa trước khi đăng. Bình luận video tiếp tục gửi riêng nếu có URL được xác minh. Kết quả gửi bình luận không rõ cần chủ Page đối chiếu trước khi thử lại.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 84 bài kiểm tra đạt. `python -m compileall -q app`: đạt. `git diff --check`: đạt. Kiểm tra không có token Meta dạng dài ngoài thư viện Hermes vendored. Sau khi restart, `/posts` và `/posts/25` trả HTTP 200; trang biên tập hiển thị bình luận đầu tiên và input chọn nhiều ảnh.

## Còn lại
Chưa thử đăng bài và bình luận thật lên Meta bằng System User; quyền gửi bình luận cần xác minh bằng một bài có kiểm soát. Bài đã đăng trước thay đổi không tự có bình luận mới. Không commit hoặc push trong nhiệm vụ này.
