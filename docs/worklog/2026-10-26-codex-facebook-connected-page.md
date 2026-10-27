# Hiển thị Facebook Page đang kết nối

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Trang Facebook cần cho thấy Page nào đang được cấu hình và xác minh kết nối, thay vì chỉ báo đã nhập thông số; không hiển thị token.

## Thực hiện
Thêm thẻ Page đang cấu hình vào `app/templates/facebook.html`, tên và ID cùng nút mở Page. `app/facebook.py` kiểm tra tên/ID qua Meta Graph API bằng token trên máy; route JSON và `app/static/facebook-page.js` cập nhật giao diện sau khi tải. Script cấu hình lưu tên Page đã xác minh gắn với ID trong biến môi trường User; trang phân biệt tên đã lưu với xác minh hiện tại. Thu gọn hướng dẫn cấu hình, cập nhật CSS, test và tài liệu. Mở lại dashboard.

## Quyết định
Không suy ra tài khoản cá nhân từ Page token. Không hiển thị hoặc ghi token; chỉ trả tên, ID và trạng thái quyền đọc. Khi token bị từ chối, vẫn hiện tên Page đã lưu từ lựa chọn trước của người dùng nhưng ghi rõ chưa xác minh lại. Tên đã lưu chỉ dùng khi ID khớp.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 75 test đạt. `node --check app/static/facebook-page.js` và `git diff --check`: đạt. GET `/facebook` trả HTTP 200. Chromium xác nhận tên Page đã lưu, Page ID, cảnh báo token và không có lỗi JavaScript. Meta trả HTTP 401 khi kiểm tra token hiện tại; giao diện hiện “Cần kiểm tra”.

## Còn lại
Token hiện tại bị Meta từ chối nên chưa xác minh tên Page hoặc quyền đăng ở thời điểm này. Chủ máy cần cấu hình lại Page token hợp lệ; chưa commit hoặc push vì không được yêu cầu.
