# Rà soát luồng xử lý và thiết kế lại giao diện

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Rà soát luồng từ nguồn tin đến bài đăng, xác định chức năng thiếu hoặc khó dùng và bổ sung trong ứng dụng Flask. Dùng hai skill `frontend-design` và `web-design-guidelines` để thiết kế lại toàn bộ giao diện, được thay font và phong cách hiện tại. Giữ an toàn dữ liệu và không tự gửi bài thật khi chưa có cấu hình.

## Thực hiện
Rà `app/web.py`, `app/database.py`, `app/discovery.py`, `app/automation.py`, `app/queue.py`, các template và ảnh chụp của 8 trang. Bổ sung trạng thái bật/tạm dừng và lần quét/lỗi gần nhất cho nguồn; nguồn tạm dừng không được quét, chọn bài mới hoặc xếp lịch từ job đang chờ, nhưng giữ tin/lịch cũ. Tải RSS/Atom qua IP công khai đã kiểm tra và cố định kết nối ở mỗi lần chuyển hướng. Bổ sung lọc tin chưa chọn viết/đã tạo bài đăng ở Bài báo, lọc/tìm hàng đợi Bài đăng và cảnh báo bài cần xử lý từ dashboard. Chặn lịch thật/đăng ngay khi thiếu Page hoặc model, giữ lịch thử nghiệm. Thêm cảnh báo khi rời trang với nội dung chưa lưu hoặc viết lại bằng AI. Viết lại `app/static/site-redesign.css` với hệ màu xanh mực/xanh dương, font Bahnschrift cục bộ, menu tối và bố cục mới; cập nhật template của toàn bộ trang, thêm `app/static/editor.js`.

## Quyết định
Giữ route và dữ liệu cũ; nâng schema bằng `ALTER TABLE` với giá trị mặc định để không mất nguồn hiện có. Tạm dừng nguồn không tự hủy lịch đã đặt. Chỉ hiển thị mã HTTP hoặc mô tả lỗi quét chung để không lộ chuỗi ngoại lệ. Bộ lọc nằm trong URL và lịch đăng được sắp theo giờ hẹn. Dùng font có sẵn trên máy, không cần tải font mạng. Quyết định dài hạn được ghi trong `contexte/decisions.md`.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 38 test đạt, gồm migration nguồn cũ, tạm dừng/quét lại, lọc bài, điều kiện lịch thật/thử nghiệm, chặn URL RSS nội bộ và chuyển hướng. Đọc thử feed Google AI công khai bằng đường tải mới: 20 mục. Dữ liệu hiện tại cho thấy 7 nguồn đã có lần quét và không có lỗi quét. Playwright: 8 trang desktop/điện thoại HTTP 200, không có lỗi JS; 9 route ở 320/390/768/1024/1440px không tràn ngang sau khi tải CSS; liên kết bỏ qua menu nhận focus, đủ 6 mục điều hướng; hộp xác nhận AI xuất hiện và hủy được mà không gửi biểu mẫu. Server localhost đã khởi động lại và trả HTTP 200. `git diff --check`, `python -m compileall -q app` và `node scripts/check-worklog.mjs`: đạt.

## Còn lại
Chưa thử với Page token/model thật. Bài kẹt ở `publishing` khi tiến trình dừng vẫn cần quy trình đối chiếu và phục hồi riêng để tránh gửi trùng. Bước nghiên cứu/xếp hạng tin theo giá trị biên tập trước khi chọn tối đa 6 bài/ngày vẫn nằm trong `PLAN.md`. Chưa commit hoặc đẩy remote vì yêu cầu hiện tại không giao thao tác Git đó.
