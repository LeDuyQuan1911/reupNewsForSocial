# Thay ảnh bài đăng kém thu hút

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thay ảnh thẻ chữ đơn điệu của bài về hợp tác OpenAI và NASK bằng ảnh minh họa thu hút hơn; cải thiện cách xử lý ảnh dự phòng cho bài sau.

## Thực hiện
Tạo ảnh minh họa AI về an toàn AI và bảo mật, không có logo/chữ/địa danh, thay ảnh đầu tiên của bản nháp #1 trong SQLite cục bộ. Thêm kiểm tra trong `app/media.py`, `app/automation.py`, `app/web.py`, `app/queue.py` để ảnh thẻ chữ đơn độc không được xếp lịch thật hoặc gửi Facebook. Thêm kiểm thử tự động trong `tests/test_automation.py`; cập nhật `SPEC.md`, `PLAN.md` và `contexte/decisions.md`.

## Quyết định
Giữ ảnh thẻ chữ như ảnh tạm để xem trước, nhưng yêu cầu thêm ít nhất một ảnh nguồn, ảnh chụp repo, ảnh tải lên hoặc ảnh AI trước khi đăng thật. Lịch thử nghiệm vẫn cho phép ảnh tạm.

## Kiểm chứng
`python -m unittest discover -s tests -p 'test_*.py'`: 48 test đạt. Flask test client: `/posts/1` và `/posts/1/image` đều HTTP 200. Kiểm tra ảnh JPEG mới bằng mắt; bản nháp #1 có `image_kind=ai_generated` và đúng một ảnh.

## Còn lại
Chưa có dịch vụ sinh ảnh tự động tại runtime; những bài không lấy được ảnh nguồn sẽ cần bổ sung ảnh trước khi đăng thật. Server cục bộ hiện không chạy; kiểm tra giao diện bằng Flask test client.
