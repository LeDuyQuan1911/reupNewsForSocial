# Thêm ảnh cho bài đăng

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thêm ảnh vào bài viết: lấy ảnh từ bài báo hoặc chụp màn hình trang repo GitHub, lưu để xem trước trên dashboard và gửi cùng nội dung lên Facebook Page. Không kết nối tài khoản Facebook thật trong nhiệm vụ này.

## Thực hiện
Đã thêm trích ảnh từ RSS/Atom và metadata Anthropic, tìm ảnh trên trang bài báo, chụp repo GitHub bằng Playwright/Chrome, và ảnh thẻ tiêu đề dự phòng. Ảnh được chuẩn hóa JPEG và lưu trong `data/media/`, cơ sở dữ liệu giữ loại ảnh và nguồn. Trang biên tập cho xem trước/lấy lại ảnh. Hàng đợi từ chối bài không có ảnh; dùng model vision duyệt cả caption và ảnh; adapter Facebook Page dùng `/photos` với ảnh và caption.

## Quyết định
Ưu tiên ảnh gốc, sau đó ảnh chụp repo, rồi thẻ tiêu đề nếu nguồn chặn truy cập. Giữ ảnh trên máy ngay từ lúc tạo nháp để lịch đăng không phụ thuộc vào ảnh online sau này. Không gửi ảnh nếu chưa qua bước kiểm duyệt văn bản và ảnh. Giới hạn URL ảnh ở HTTPS công khai, giới hạn dung lượng và chuẩn hóa qua Pillow trước khi lưu.

## Kiểm chứng
Đã kiểm tra chụp `https://github.com/psf/requests` bằng Chrome headless: nhận ảnh PNG và chuyển JPEG được. Bài OpenAI công khai trả 403 với HTTP client và Chrome headless; ảnh thẻ tiêu đề xử lý trường hợp này. Bài Google AI tải được ảnh nguồn. Dashboard đang chạy đã phục vụ ảnh và trang biên tập HTTP 200, ảnh tải trong Chrome và bố cục đã xem qua screenshot. `python -m unittest discover -s tests -v`: 15/15 qua; `python -m compileall -q app run.py` qua. Review độc lập được thực hiện trước bàn giao.

## Còn lại
Chưa có token Page hoặc model vision để xác nhận đăng ảnh thật. Nếu Chrome không có hoặc nguồn bài báo chặn tải ảnh, hệ thống dùng ảnh thẻ tiêu đề. Bộ lọc LLM không thể bảo đảm tuyệt đối phù hợp mọi chính sách nền tảng.
