# Bỏ tiêu đề giới thiệu trên trang Tổng quan

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Xóa ba dòng “TỔNG QUAN”, “Bàn điều khiển” và mô tả ngay dưới khỏi trang Tổng quan. Giữ nút “Tìm bài mới” và các phần nội dung khác.

## Thực hiện
Đã xóa ba dòng khỏi `app/templates/dashboard.html`, giữ nút “Tìm bài mới” ở góc phải bằng `app/static/style.css`. Cập nhật `tests/test_app.py` để bỏ kỳ vọng tiêu đề cũ và xác nhận phần giới thiệu không còn trong HTML.

## Quyết định
Giữ nút tìm bài và các thẻ thống kê ở vị trí cũ; chỉ bỏ phần giới thiệu người dùng nêu.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 19/19 test đạt. `git diff --check`: đạt. Kiểm tra template xác nhận ba dòng đã được bỏ.

## Còn lại
Chưa review độc lập hoặc tạo PR; cần hoàn tất quy trình review trước khi merge vào `main`.
