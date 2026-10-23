# Tách dashboard thành nhiều trang

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Tách giao diện đang gộp thành trang Dashboard, Tài khoản, Nguồn thông tin và Bài báo; giữ luồng bản nháp, lịch đăng và ảnh hiện có.

## Thực hiện
Tạo layout/điều hướng chung và các trang riêng cho tổng quan, bài báo (danh sách, chi tiết, tìm kiếm/lọc/phân trang), bài đăng (phân trang), nguồn thông tin và tài khoản/kết nối. Trang biên tập dùng layout mới. Thêm truy vấn thống kê, bộ lọc và truy vấn bài đăng theo article ID trong SQLite; cập nhật README, MAP, SPEC, PLAN và test route. Xử lý ba phát hiện của review độc lập: giới hạn trang, lịch sử bài đăng quá 10.000 và ký tự `%`/`_` trong tìm kiếm.

## Quyết định
Giữ trạng thái tài khoản ở mức biến môi trường đã đặt; không hiển thị token và không tạo luồng login vì người dùng đã hoãn kết nối. Dashboard chỉ hiển thị tóm tắt để giảm độ dài; dữ liệu chi tiết ở từng trang.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 19 test qua. `python -m compileall -q app run.py`: qua. Playwright mở tổng quan, bài báo, tài khoản, biên tập trên ứng dụng localhost; mobile 390px không tràn ngang. Đã xem ảnh chụp giao diện desktop/mobile. URL có số trang rất lớn trả 200 sau sửa.

## Còn lại
Chưa kiểm tra đăng Facebook/LLM thực tế vì chưa có cấu hình của chủ dự án. Trang tài khoản chỉ phản ánh cấu hình biến môi trường, không xác minh kết nối. Reviewer đã đối chiếu bản sửa; chưa merge.
