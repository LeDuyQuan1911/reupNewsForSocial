# Header chung cho bảng hoạt động theo ngày

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Chỉ hiển thị nhãn cột một lần ở đầu danh sách hoạt động theo ngày của trang Tổng quan; các dòng ngày chỉ hiển thị giá trị. Giữ bố cục dễ đọc trên điện thoại.

## Thực hiện
Đổi danh sách trong `app/templates/dashboard.html` thành bảng với một hàng tiêu đề và một dòng cho mỗi ngày. Cập nhật `app/static/ui-refresh.css` để các cột thẳng hàng, cuộn ngang trong vùng bảng trên điện thoại. Cập nhật kiểm tra trong `tests/test_app.py` và ghi yêu cầu/tiến độ trong `SPEC.md`, `PLAN.md`.

## Quyết định
Dùng bảng HTML để header cột liên kết rõ với giá trị từng ngày và hỗ trợ trình đọc màn hình.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 31/31 đạt. `git diff --check`: đạt. Kiểm tra trình duyệt ở 1440px và 390px: 5 header, 7 dòng, trang không tràn ngang; bảng cuộn ngang ở 390px. Khởi động lại server và xác nhận `http://127.0.0.1:5000/` trả HTTP 200, chứa bảng mới.

## Còn lại
Không có.
