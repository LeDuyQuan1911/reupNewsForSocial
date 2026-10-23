# Bỏ khối giới thiệu trên năm trang

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Theo năm ảnh người dùng gửi, bỏ các khối nhãn, tiêu đề lớn và mô tả đầu trang của Tổng quan, Bài báo, Bài đăng, Nguồn thông tin và Tài khoản & kết nối. Giữ các thao tác trên trang.

## Thực hiện
Giữ thay đổi cục bộ đã bỏ khối Tổng quan; bỏ khối tương ứng trong `articles.html`, `posts.html`, `sources.html`, `account.html`. Dùng lớp `page-actions` trong CSS để căn phải nút tìm bài và liên kết chọn bài báo. Cập nhật test trang để kiểm tra nội dung còn lại và xác nhận không còn khối `page-heading` ở năm trang.

## Quyết định
Giữ nút tìm bài và liên kết chọn bài báo sau khi bỏ phần giới thiệu.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 19/19 test đạt. `git diff --check`: đạt. `rg` xác nhận các dòng mô tả được nêu trong ảnh không còn trong template.

## Còn lại
Chưa review độc lập hoặc tạo PR; cần hoàn tất review trước khi merge vào `main`.
