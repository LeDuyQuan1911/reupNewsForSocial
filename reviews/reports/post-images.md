# Báo cáo review: post-images

- Reviewer: Codex (review độc lập)
- Ngày: 2026-10-23
- Base / head: 5819b4e074af8ecc7eaf5319c5193adf6fbeb2dd / 721cbf38e6f22c20b669fe702f48da9a22fb4ca5
- Vòng: đối chiếu
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff base/head, nhất là `app/media.py`, `app/feeds.py`, `app/database.py`, `app/llm.py`, `app/facebook.py`, `app/queue.py`, `app/web.py`, template ảnh và `tests/test_app.py`; đối chiếu `SPEC.md`.
- Lệnh đã chạy và kết quả: `python -B -m unittest discover -s tests -v` (15/15 qua); `python -m compileall -q app run.py` (qua); một tình huống tái hiện có kiểm soát cho race lấy lại ảnh/đăng (xác nhận ảnh được duyệt khác ảnh được gửi).
- Phần chưa kiểm chứng: Không gọi dịch vụ LLM, trang báo hoặc Facebook Page thật; không thử khai thác DNS rebinding trên mạng thật.

## Phát hiện

### P1 — Ảnh có thể bị thay sau khi duyệt nhưng trước khi đăng

- Vị trí: `app/media.py:199` và `app/queue.py:31`
- Điều kiện kích hoạt / cách tái hiện: Bắt đầu lấy lại ảnh khi bài còn `draft`, giữ yêu cầu tải ảnh; sau đó bấm đăng ngay để `claim_post` đổi trạng thái thành `publishing`. Để `llm.check_post` đọc ảnh cũ, rồi cho thao tác lấy lại ảnh hoàn tất trước khi `facebook.publish_page` đọc file.
- Kết quả thực tế: `prepare_post_image` ghi đè `post-<id>.jpg` trước khi `database.attach_image` kiểm tra trạng thái và báo lỗi. Facebook đọc file mới, chưa được model duyệt. Tái hiện cho kết quả pixel được duyệt `(254, 0, 0)`, pixel được gửi `(0, 0, 254)`, trạng thái cuối `published`.
- Kết quả mong đợi: File ảnh gửi Page phải đúng byte đã qua kiểm duyệt; thao tác thay ảnh đang đăng không được ghi đè file đó.
- Bằng chứng: `media.prepare_post_image` đọc trạng thái ở dòng 167-172, ghi đè ở 198-199, rồi mới gọi `database.attach_image` ở 200. `queue.process_claimed_post` duyệt theo đường dẫn ở 30 rồi `facebook.publish_page` đọc lại cùng đường dẫn ở 39. Thử nghiệm luồng đồng thời trong checkout review xác nhận đường đua này.
- Độ chắc chắn: cao
- Hướng sửa gợi ý (nếu có): Dùng file ảnh bất biến theo phiên bản, xác nhận trạng thái và cập nhật tham chiếu DB trước khi thay file; hoặc gửi chính byte đã được duyệt.

### P2 — Kiểm tra IP và kết nối ảnh dùng hai lần phân giải DNS

- Vị trí: `app/media.py:40` và `app/media.py:52`
- Điều kiện kích hoạt / cách tái hiện: Feed hoặc metadata bài báo trỏ đến tên miền HTTPS do bên ngoài kiểm soát, trả IP công khai khi `socket.getaddrinfo` kiểm tra, rồi trả IP nội bộ khi `urllib` tự phân giải để kết nối.
- Kết quả thực tế: `validate_public_url` chỉ kiểm tra tập IP tại thời điểm gọi; `opener.open(request)` kết nối theo hostname và không dùng các địa chỉ đã kiểm tra. Vì vậy chặn mạng riêng có thể bị vượt qua bằng DNS rebinding, khiến ứng dụng trên máy cá nhân gửi GET tới dịch vụ nội bộ. Đây là rủi ro suy ra trực tiếp từ hai lệnh phân giải độc lập; chưa thử khai thác mạng thật.
- Kết quả mong đợi: Kết nối ảnh/trang nguồn chỉ đến địa chỉ công khai đã được xác thực, kể cả sau chuyển hướng.
- Bằng chứng: `validate_public_url` tại 40-42 gọi `getaddrinfo`; `fetch_public_bytes` tại 49-52 tạo request bằng hostname rồi gọi `opener.open` mà không ghim IP hoặc kiểm tra địa chỉ kết nối. Mỗi chuyển hướng lại lặp cùng mẫu.
- Độ chắc chắn: vừa
- Hướng sửa gợi ý (nếu có): Dùng client cho phép ghim IP đã kiểm tra khi kết nối TLS vẫn xác thực hostname, và kiểm tra từng chuyển hướng.

## Đối chiếu sau phản hồi tác giả

Đối chiếu bản sửa chưa commit trong checkout chính ngày 2026-10-23; hai phát hiện ban đầu vẫn được giữ ở trên làm dấu vết review.

- **P1 — đã sửa trong bản chưa commit.** `queue.process_claimed_post` đọc JPEG một lần thành `bytes` và truyền chính đối tượng byte đó vào `llm.check_post` và `facebook.publish_page`; hai hàm không đọc lại đường dẫn. `media.prepare_post_image` tạo tên file UUID riêng, cập nhật DB sau khi ghi file, và xóa file mới nếu cập nhật bị từ chối. Test mới `test_publishes_exact_image_bytes_reviewed` đổi file trên đĩa sau lúc kiểm duyệt nhưng xác nhận Page vẫn nhận byte cũ. Đường đua ban đầu không còn gửi ảnh chưa duyệt.
- **P2 — đã sửa trong bản chưa commit.** `validate_public_url` trả IP công khai đã xác minh; `fetch_public_bytes` truyền IP đó cho `PinnedHTTPSConnection`, nơi `socket.create_connection` kết nối trực tiếp tới IP và TLS vẫn dùng hostname cho SNI/xác thực chứng chỉ. Mỗi lần chuyển hướng được kiểm tra lại. Test mới kiểm tra IP đã duyệt được truyền vào connection. Chưa kiểm tra trên DNS rebinding thật hoặc proxy mạng thật.
- Kiểm chứng checkout chính: `python -B -m unittest discover -s tests -v` (17/17 qua), `python -m compileall -q app run.py` (qua).

## Kết luận cho chủ repo

Hai phát hiện P1/P2 đã được xử lý trong bản sửa chưa commit của checkout chính theo đối chiếu source và test. Còn giới hạn là chưa thử dịch vụ LLM, Facebook Page hay DNS rebinding thật. Reviewer không quyết định merge.
