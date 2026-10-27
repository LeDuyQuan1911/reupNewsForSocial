# Chọn giờ đăng bằng đồng hồ

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thay ô nhập chuỗi giờ đăng bằng các ô chọn giờ trực quan, một giờ cho mỗi bài trong trang điều khiển Hermes. Số ô phải theo số bài/ngày; giữ kiểm tra lịch hiện có.

## Thực hiện
Thay trường văn bản giờ đăng trong `app/templates/hermes.html` bằng các ô `type=time`, mỗi bài một ô, có nút mở bộ chọn giờ. `app/static/posting-times.js` cập nhật số ô theo số bài/ngày và giữ giờ đã chọn khi thay đổi số lượng. `app/web.py` nhận danh sách giờ rồi dùng bộ kiểm tra hiện có. Cập nhật CSS, test, README, MAP, SPEC và PLAN; mở lại server.

## Quyết định
Dùng bộ chọn giờ gốc của trình duyệt để thao tác bằng đồng hồ và giữ bàn phím/trợ năng sẵn có. Các giờ gợi ý cho ô mới cách giờ hiện có ít nhất 30 phút; server tiếp tục kiểm tra cuối cùng trước khi lưu. Giữ endpoint lưu lịch cũ để tương thích.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 74 test đạt. `node --check app/static/posting-times.js`: đạt. `git diff --check`: đạt. Chromium headless xác nhận trang hiển thị 6 ô giờ, tăng 8/giảm 3 ô đúng và giữ giá trị đầu; đã xem ảnh chụp desktop và điện thoại. GET `/hermes`: HTTP 200.

## Còn lại
Giao diện đồng hồ phụ thuộc trình duyệt và thiết lập vùng/ngôn ngữ của máy; giá trị lưu vẫn là 24 giờ Bangkok. Chưa commit hoặc push vì không được yêu cầu.
