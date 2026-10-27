# Cải thiện trang Luồng đăng

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Làm trang Luồng đăng dễ hiểu và dễ thao tác hơn, giữ rõ nguồn → bài báo → bài đăng/kênh → thời điểm. Theo yêu cầu mới, tìm và dùng skill thiết kế giao diện phù hợp.

## Thực hiện
Cài `frontend-design` từ `anthropics/skills` và `web-design-guidelines` từ `vercel-labs/agent-skills` bằng skill-installer; đọc nội dung và hướng dẫn UI mới nhất. Thay các thẻ lặp bốn bước trong `app/templates/workflow.html` bằng bảng ưu tiên tiêu đề, nguồn, trạng thái, kênh, thời gian và thao tác. Cập nhật `app/static/ui-refresh.css` để bảng gọn trên desktop và thành mục riêng trên điện thoại. Cập nhật kiểm tra trong `tests/test_app.py`, mô tả trong `README.md`, `MAP.md`, `SPEC.md`, `PLAN.md`.

## Quyết định
Giữ hai chế độ xem hiện có. Đưa tiêu đề bài lên trước, chỉ có một hàng tên cột trên desktop; điện thoại hiển thị tiêu đề, trạng thái, nơi đăng, giờ và nút mở theo thứ tự dễ đọc. Dùng bảng HTML có header và row header để giữ ngữ nghĩa truy cập.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 32/32 đạt. `git diff --check`: đạt. Trang `/workflow` trả HTTP 200. Playwright kiểm tra 1440px và 390px: 5 tiêu đề cột, 19 dòng dữ liệu, không tràn ngang; sửa một lỗi tiêu đề bị hẹp ở mobile sau khi xem ảnh chụp. Đối chiếu UI với hướng dẫn truy cập và điều hướng của Vercel.

## Còn lại
Không có. Hai skill mới được cài trong thư mục Codex cá nhân và sẽ tự hiện ở các lượt làm việc tiếp theo; chưa commit thay đổi repo.
