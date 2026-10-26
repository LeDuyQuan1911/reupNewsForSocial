# Làm mới giao diện dashboard

- Ngày: 2026-10-25
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn giao diện dashboard đẹp hơn và dễ sử dụng hơn trên các trang chính, nhất là luồng đăng và biên tập bài.

## Thực hiện
Khảo sát giao diện desktop/mobile bằng Playwright. Thêm lớp CSS responsive mới và cập nhật khung điều hướng, trang luồng, danh sách bài đăng, dashboard và trang biên tập. Luồng đăng gọn hơn, cho thấy trạng thái và lối mở bài; trang biên tập đưa nội dung lên trước ảnh, hiển thị trọn nội dung bài đã lên lịch và trình bày lịch thử nghiệm rõ ràng. Cập nhật `MAP.md`, `SPEC.md`, `PLAN.md` theo thay đổi.

## Quyết định
Giữ các route, thao tác và ràng buộc đăng hiện có; tập trung vào thứ tự thông tin, phân cấp thị giác và khả năng đọc trên màn hình nhỏ. Dùng CSS cục bộ, không thêm phụ thuộc hoặc dịch vụ ngoài.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 30/30 test đạt. Flask test client trả HTTP 200 trên bảy trang chính. Playwright chụp dashboard, luồng đăng và trang biên tập ở 1440px/390px; không tràn ngang. Server localhost:5000 được khởi động lại, `GET /posts/6` trả HTTP 200 và tải lớp CSS mới.

## Còn lại
Chưa có review độc lập cho diff giao diện này; cần review trước khi merge vào `main` theo plugin đang bật. Không có thử nghiệm thao tác đăng Facebook thật.
