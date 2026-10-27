# Chỉnh màu header và điều hướng

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng thấy header và nav xanh đậm hiện tại không hợp với giao diện nội dung sáng. Chỉnh lại màu, độ nổi bật và trạng thái chọn/hover/focus của phần khung chung trên desktop và điện thoại.

## Thực hiện
Đọc CSS khung trang và ảnh người dùng. Đổi `app/static/site-redesign.css`: header nền trắng có đường viền mảnh, nav nền sáng hòa với canvas, mục đang chọn nền trắng/xanh nhạt cùng dấu xanh dương; thay dấu thương hiệu xanh ngọc bằng xanh dương. Cập nhật màu trình duyệt và ẩn chữ R trang trí khỏi tên liên kết trong `app/templates/base.html`. Ghi yêu cầu và bước hoàn tất vào `SPEC.md`, `PLAN.md`.

## Quyết định
Giữ màu xanh dương đã dùng ở nút/liên kết làm điểm nhấn duy nhất trong khung trang. Dùng nền trung tính cho header/nav để bảng nội dung là phần chính; không đổi chức năng điều hướng.

## Kiểm chứng
Chromium headless mở `/workflow` ở 1440×900, 768×900 và 390×844: sáu mục điều hướng hiện đủ, không tràn ngang toàn trang. Xem ảnh chụp tại cả ba kích thước. Màu chữ trên nền tương ứng đạt tương phản 5,65:1 (nav), 8,37:1 (mục chọn desktop), 7,38:1 (mục chọn điện thoại), 5,84:1 (nhãn header). Kiểm tra hướng dẫn UI hiện hành từ nguồn của skill. Chạy `git diff --check` và `node scripts/check-worklog.mjs` trước khi bàn giao.

## Còn lại
Không có trong phạm vi đổi màu header/nav. Chưa commit vì yêu cầu hiện tại không yêu cầu commit.
