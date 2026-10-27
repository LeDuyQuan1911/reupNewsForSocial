# Điều kiện chạy Facebook tự động

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích cách đưa hệ thống hiện tại tới trạng thái tự đăng, sau khi đã có trang chọn nhóm Facebook.

## Thực hiện
Kiểm tra số nhóm đã lưu/chọn, trạng thái biến môi trường ở dạng có/không, cổng dashboard/9Router và luồng chạy lịch trong source. Không truy cập tài khoản Facebook, không đăng bài và không sửa luồng đăng.

## Quyết định
Tách đường đăng Page hiện có khỏi yêu cầu đăng nhóm. Không bật cơ chế đăng nhóm khi chưa có nhóm đích, danh tính đăng, phiên đăng nhập và adapter kiểm chứng được.

## Kiểm chứng
Database hiện có 0 nhóm; `REUP_AUTO_ENABLED=1`, model và key đã đặt; cổng 5000 và 20128 lắng nghe. Page ID, Page token và phiên bản Graph API chưa đặt. Source `run.py`, `app/automation.py` và `app/facebook.py` xác nhận chỉ tự đăng Page, chưa dùng bảng nhóm.

## Còn lại
Để Page đăng: người dùng cần Page và token có quyền phù hợp. Để nhóm đăng: cần thêm ít nhất một URL nhóm, xác định tài khoản/Page đăng, đăng nhập thủ công và triển khai/kiểm thử adapter trình duyệt cùng lịch xử lý lỗi. Không yêu cầu gửi mật khẩu/token qua chat.
