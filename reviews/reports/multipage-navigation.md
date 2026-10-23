# Báo cáo review: multipage-navigation

- Reviewer: Codex (agent độc lập)
- Ngày: 2026-10-23
- Base / head: abce4486cd0995f3f3fc3c45ee0ca785ddb90f90 / 1dfdddbf795387aa3ea3fb6a0e82594cfbdab896
- Vòng: đối chiếu
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff của `app/web.py`, `app/database.py`, `app/templates/`, `app/static/style.css`, `tests/test_app.py`; các trang tổng quan, bài báo, bài đăng, nguồn, tài khoản; luồng tạo nháp, ảnh, lịch đăng và đăng ngay. Lượt đầu chưa đọc worklog tác giả.
- Lệnh đã chạy và kết quả: `python -m unittest discover -s tests -v` tại head: 18 test đạt; sau bản sửa chưa commit: 19 test đạt. Tái hiện riêng lỗi page quá lớn và tìm kiếm ký tự `%` bằng Flask test client/SQLite tạm.
- Phần chưa kiểm chứng: chưa chạy thao tác thật với LLM, Facebook Page hoặc tải nguồn ngoài; chưa kiểm tra bằng trình duyệt trực quan. Worktree review chỉ đọc nên test và báo cáo được thực hiện trong checkout chính theo phân công của người điều phối.

## Phát hiện lượt độc lập

### P2 — Page quá lớn gây lỗi 500

- Vị trí: `app/web.py:52` tại head.
- Điều kiện kích hoạt / cách tái hiện: GET `/articles?page=999999999999999999999`.
- Kết quả thực tế: HTTP 500 do `OverflowError` khi offset chuyển sang SQLite INTEGER.
- Kết quả mong đợi: trang hợp lệ hoặc phản hồi lỗi tham số có kiểm soát.
- Bằng chứng: tái hiện bằng Flask test client, traceback ở `app/database.py:114`.
- Độ chắc chắn: cao.

### P2 — Lịch sử bài đăng bị giới hạn 10.000 mục

- Vị trí: `app/web.py:82` và `app/web.py:72` tại head.
- Điều kiện kích hoạt / cách tái hiện: cơ sở dữ liệu có hơn 10.000 bài đăng.
- Kết quả thực tế: `/posts` chỉ hiển thị 10.000 bài mới nhất và không có phân trang; trang chi tiết bài báo có thể không tìm thấy bài đăng cũ để hiện liên kết biên tập.
- Kết quả mong đợi: có thể truy cập mọi bài đăng và nhận biết đúng bài đã có bản nháp.
- Bằng chứng: cả hai route dùng `list_posts(..., limit=10000)`; template bài đăng tại head không có phân trang.
- Độ chắc chắn: cao theo đường code; chưa tạo dữ liệu 10.001 bài để kiểm tra trình duyệt.

### P3 — Tìm kiếm coi `%` và `_` là ký tự đại diện

- Vị trí: `app/database.py:103` tại head.
- Điều kiện kích hoạt / cách tái hiện: tìm `100%` khi chỉ có bài mang tiêu đề `1000 users`.
- Kết quả thực tế: bài đó vẫn được trả về.
- Kết quả mong đợi: tìm chính xác chuỗi ký tự thường `100%`.
- Bằng chứng: `LIKE` chưa escape `%` và `_`; tái hiện trong SQLite tạm.
- Độ chắc chắn: cao.

## Đối chiếu sau phản hồi tác giả

- Lỗi page quá lớn: **đã sửa trong thay đổi chưa commit**. `web.py` giới hạn độ dài tham số, ép page vào khoảng trang hiện có; test GET page quá lớn trả 200.
- Giới hạn 10.000 bài: **đã sửa trong thay đổi chưa commit**. `/posts` dùng tổng số bài và phân trang 25 mục; trang bài báo tra cứu trạng thái nháp theo các ID trên trang, chi tiết bài báo tra cứu trực tiếp theo `article_id`. Test 27 bài xác nhận trang 2 và truy vấn trực tiếp.
- Tìm kiếm ký tự đại diện: **đã sửa trong thay đổi chưa commit**. `database.py` escape `\\`, `%`, `_` và dùng `ESCAPE '\\'`; test tìm `100%` chỉ trả bài có ký tự `%` thật.

## Kết luận cho chủ repo

Ba phát hiện ở commit head đã có bản sửa chưa commit và 19 test hiện đạt. Chưa có phát hiện còn mở trong phạm vi đối chiếu này. Cần xem diff cuối cùng sau khi commit và tự kiểm tra tích hợp thật với dịch vụ ngoài khi có cấu hình phù hợp. Reviewer không quyết định merge.
