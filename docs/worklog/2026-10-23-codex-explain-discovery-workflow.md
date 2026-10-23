# Giải thích workflow tìm bài

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích cách ứng dụng hiện tại tìm bài viết và đưa bài vào luồng đăng.

## Thực hiện
Đã đối chiếu `app/web.py`, `app/database.py`, các adapter `app/feeds.py`, `app/anthropic.py`, `app/github.py` và giao diện Bài báo/Luồng đăng. Luồng tìm bài được kích hoạt thủ công qua nút “Tìm bài mới”, quét nguồn có sẵn và RSS/Atom tự thêm, lưu metadata bài theo URL duy nhất, rồi chuyển đến danh sách có tìm kiếm/lọc nguồn. Bài được chọn mới tạo bản nháp và xuất hiện trong luồng đăng mặc định.

## Quyết định
Chỉ mô tả hành vi có trong code hiện tại; không gọi trang Luồng đăng là bộ máy tự tìm bài. Không ngầm hiểu app đã đọc toàn văn hay quét X.

## Kiểm chứng
Đối chiếu route `POST /discover`, các hàm fetch và `save_articles`, nút trong template và query `list_publication_workflows`. Không chạy quét mạng vì yêu cầu chỉ hỏi cách dùng, không yêu cầu tìm bài ngay.

## Còn lại
Không có thay đổi chức năng. Khả năng tự động quét theo lịch, đọc toàn văn bài gốc và nguồn X chưa được triển khai trong luồng hiện tại.
