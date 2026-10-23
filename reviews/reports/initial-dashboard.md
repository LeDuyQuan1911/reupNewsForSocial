# Báo cáo review: initial-dashboard

- Reviewer: Codex (agent review độc lập)
- Ngày: 2026-10-23
- Base / head: `5c78369fcead12bd1356073d80b7a22b0e5b2efd` / `61e175372fd94b5b5e5f555cd80d9527e71012c9`
- Vòng: độc lập
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: `SPEC.md`, `README.md`, `MAP.md`, `PLAN.md`; toàn bộ `app/`, `run.py`, `.env.example`, `requirements.txt`, `tests/test_app.py`; tập trung tạo nguồn, khử trùng URL, bản nháp, lịch, kiểm duyệt, chống đăng tin tương tự và Facebook Page. Phần `vendor/` là upstream, không review chi tiết.
- Lệnh đã chạy và kết quả: `node scripts/plugins.mjs check` hợp lệ; `python -m unittest discover -s tests -v` tại checkout mới thất bại cả 6 test do thiếu `data/`; chạy cùng bộ test với `PYTHONPATH` trỏ checkout và thư mục tạm có `data/` thì 6/6 qua. Kiểm chứng riêng bằng mock cho thấy timeout sau `facebook.publish_page` đặt trạng thái `failed` và `claim_post` cho phép gửi lại.
- Phần chưa kiểm chứng: LLM/9Router và Facebook Page token thật; khả năng tiếp nhận bài từ RSS/Anthropic/GitHub qua mạng; mã upstream trong `vendor/`. Ban đầu môi trường hạn chế truy cập metadata Git tại checkout; sau khi được cấp quyền đọc, `git status --short --branch` xác nhận chỉ có report và reviewer worklog mới, `git diff --check` không báo lỗi. Head được xác nhận qua `git rev-parse HEAD`.

## Phát hiện

### P1 — Timeout sau khi gửi Facebook cho phép đăng lại cùng bài

- Vị trí: `app/queue.py:34-36`, `app/database.py:174-179`
- Điều kiện kích hoạt / cách tái hiện: Facebook đã nhận POST nhưng client mất phản hồi hoặc hết thời gian chờ tại `urlopen`; người dùng bấm “Đăng ngay” lần nữa hoặc lên lịch lại bài lỗi.
- Kết quả thực tế: mọi exception của `publish_page` chuyển `publishing` thành `failed`; `claim_post` chấp nhận `failed`, nên một request POST thứ hai có thể tạo bài trùng. Mock `publish_page` ném `TimeoutError('response lost')` cho kết quả `after uncertain send: failed`, `reclaimable for second send: True`.
- Kết quả mong đợi: kết quả gửi không xác định được phải giữ trạng thái cần đối chiếu thủ công, tránh cho gửi lại trước khi xác nhận Page có bài hay chưa; README cũng mô tả bài chưa xác nhận ở `publishing`.
- Bằng chứng: `app/facebook.py:21-26` đọc phản hồi sau POST; lỗi đọc hoặc timeout có thể phát sinh sau khi server đã nhận request. `app/queue.py:35-36` không phân biệt lỗi trước và sau khi gửi. Test hiện tại chỉ bao phủ đường thành công và kiểm duyệt chặn.
- Độ chắc chắn: cao về trạng thái và khả năng gửi lại; vừa về việc Page đã nhận request trong một timeout cụ thể.
- Hướng sửa gợi ý (nếu có): phân biệt lỗi cấu hình/kiểm duyệt trước khi gửi với kết quả mạng không xác định sau khi gửi; để bài ở trạng thái chờ đối chiếu, chỉ cho retry khi người dùng đã xác nhận.

### P2 — Bộ test không chạy được trên checkout sạch

- Vị trí: `tests/test_app.py:21`
- Điều kiện kích hoạt / cách tái hiện: clone hoặc worktree mới chưa chạy ứng dụng, không có `data/` vì `.gitignore` bỏ qua cả thư mục; chạy lệnh test được README hướng dẫn.
- Kết quả thực tế: cả 6 test lỗi `FileNotFoundError` tại `tempfile.TemporaryDirectory(dir='data')` trước khi vào hành vi cần test.
- Kết quả mong đợi: test tự tạo thư mục tạm cần thiết hoặc dùng thư mục tạm hệ thống để lệnh kiểm tra chạy được ngay trên checkout sạch.
- Bằng chứng: `tests/test_app.py:21`; lệnh `python -m unittest discover -s tests -v` tại checkout trả `FAILED (errors=6)`. Cùng source test qua hết khi có `data/` ở thư mục chạy.
- Độ chắc chắn: cao.
- Hướng sửa gợi ý (nếu có): dùng `TemporaryDirectory()` mặc định hoặc tạo `data/` trong fixture.

## Đối chiếu sau phản hồi tác giả

Đã đối chiếu các thay đổi chưa commit trong checkout chính ngày 2026-10-23, không sửa implementation.

- **P1: đã xử lý cho timeout/exception từ Facebook.** `app/queue.py:37-47` đưa lỗi sau khi gọi `facebook.publish_page` về `uncertain`; `app/database.py:175-180` không cho claim trạng thái này. Giao diện `app/templates/post.html:40-48` yêu cầu người dùng kiểm tra Page rồi mới đánh dấu đã đăng hoặc trở về nháp qua `app/web.py:167-180`. Test mới `tests/test_app.py:112-131` xác nhận timeout để bài ở `uncertain`, không claim lại và có đường đánh dấu đã đăng. Giới hạn còn lại: nếu tiến trình chết khi trạng thái là `publishing`, ứng dụng chưa có nút đối chiếu trạng thái này; README hướng dẫn kiểm tra thủ công trong database.
- **P2: đã xử lý.** `tests/test_app.py:21` tạo thư mục tạm dưới `tests/`, nên không phụ thuộc `data/`. Chạy `python -m unittest discover -s tests -v` tại checkout chính: 7/7 qua.
- `git diff --check` không báo lỗi nội dung; Git chỉ cảnh báo chuyển LF sang CRLF ở working copy. Chưa kiểm thử với Facebook Page hoặc LLM thật.

## Kết luận cho chủ repo

Hai phát hiện ban đầu đã được tác giả xử lý và reviewer đối chiếu trên thay đổi chưa commit; 7/7 test qua. Còn rủi ro tiến trình dừng khi `publishing` cần đối chiếu thủ công trong database, và chưa xác minh với dịch vụ thật.
