# Làm lại giao diện toàn bộ dashboard

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Áp dụng hai skill `frontend-design` và `web-design-guidelines` để cải thiện đồng bộ toàn bộ trang web Flask: Tổng quan, Bài báo, chi tiết bài báo, Luồng đăng, Bài đăng, biên tập bài đăng, Nguồn thông tin và Tài khoản. Giữ các hành vi dữ liệu, lịch và xuất bản hiện có.

## Thực hiện
Khảo sát 8 trang ở kích thước desktop và điện thoại. Thêm `app/static/site-redesign.css` để thống nhất màu, chữ, khoảng cách, biểu mẫu, bảng, menu và trạng thái; giảm trang trí dư thừa. Sửa `base.html` để liên kết stylesheet và thêm liên kết bỏ qua menu bằng bàn phím. Sắp lại nội dung ở `articles.html`, `article.html`, `posts.html`, `post.html`, `sources.html` và `account.html`, trong đó trang Tài khoản gom trạng thái tự động hóa và kết nối thành hai nhóm dễ đọc. Thêm kích thước ảnh, tải lười và xác nhận trước khi bỏ ảnh ở trang biên tập. Cập nhật `MAP.md`, `SPEC.md`, `PLAN.md` và điều chỉnh một kỳ vọng HTML trong `tests/test_app.py`.

## Quyết định
Giữ các route, biểu mẫu và xử lý dữ liệu hiện có. Dùng lớp CSS riêng sau hai stylesheet cũ để thay đổi giao diện có thể kiểm tra và hoàn tác độc lập. Trên điện thoại, menu hiển thị sáu mục trong hai hàng để không ẩn mục phía ngoài màn hình. Trang Tổng quan tiếp tục ưu tiên số liệu theo ngày; không thêm lại phần giới thiệu lớn hoặc danh sách tin.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 32 test đạt. `git diff --check`: đạt. Mở 8 route ở 1440px và 390px: đều HTTP 200, không tràn ngang; đã xem ảnh chụp các trang Tổng quan, Bài báo, Luồng đăng, Bài đăng, Nguồn thông tin và Tài khoản. Server cục bộ đã khởi động lại và `/` trả HTTP 200 với stylesheet mới.

## Còn lại
Chưa kiểm thử kết nối Facebook Page hoặc model thật vì nhiệm vụ này chỉ thay đổi giao diện. Các thay đổi đang ở nhánh làm việc, chưa commit theo phạm vi yêu cầu hiện tại.
