# Tăng tốc trang Hermes

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Tìm và sửa nguyên nhân trang Hermes tải rất chậm; giữ trạng thái và nút điều khiển chính xác.

## Thực hiện
Đo trang `/hermes` cũ mất 9,17 giây vì ba lệnh Hermes CLI chạy nối tiếp. Chuyển đọc trạng thái sang `/hermes/status`, tải bằng `app/static/hermes-status.js` sau khi trang hiện; chạy ba lệnh đọc CLI song song trong `app/hermes_control.py`. Nút điều khiển chỉ bật sau khi xác nhận trạng thái. Cập nhật template, test, README, MAP, SPEC và PLAN; mở lại dashboard.

## Quyết định
Ưu tiên thời gian xuất hiện trang và cấu hình lịch; trạng thái Hermes tải bất đồng bộ, không chặn điều hướng. Tiếp tục xác thực ID, script và workdir trước mọi thao tác điều khiển; không thay luồng đăng tự động.

## Kiểm chứng
Trước sửa: GET `/hermes` 9,17 giây. Sau sửa: GET `/hermes` HTTP 200 trong 0,11 giây; API trạng thái trả `active`, gateway đang chạy và 5 lượt gần đây trong 4,1 giây. Chromium xác nhận trang xuất hiện, trạng thái/nút/lịch sử cập nhật và không có lỗi JavaScript. `python -m unittest discover -s tests -q`: 74 test đạt. `node --check app/static/hermes-status.js` và `git diff --check`: đạt.

## Còn lại
Khi vừa vào trang, trạng thái hiện “Đang kiểm tra” vài giây trước khi nút điều khiển được bật. Chưa commit hoặc push vì không được yêu cầu.
