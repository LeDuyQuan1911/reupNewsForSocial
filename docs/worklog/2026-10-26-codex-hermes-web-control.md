# Website điều khiển Hermes

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cho người dùng kiểm soát job Hermes của repo trong website: xem trạng thái/lần chạy, chạy một lượt, tạm dừng/tiếp tục và tới phần đặt lịch; không hiển thị secrets hoặc cho nhập lệnh tùy ý.

## Thực hiện
Thêm `app/hermes_control.py` để đọc gateway, lịch sử cron và xác thực job bằng ID, script, workdir trước khi thao tác. Thêm route và trang `/hermes` với chạy một lượt, tạm dừng/tiếp tục, đặt số bài/giờ đăng và quét nguồn thủ công. Cập nhật điều hướng, dashboard, tài liệu và test. Khởi động lại dashboard để nạp route mới.

## Quyết định
Chỉ chấp nhận ba thao tác Hermes cố định; không nhận câu lệnh tùy ý từ web. Giữ job ID và trạng thái cục bộ ngoài Git. Giữ route lưu lịch cũ để biểu mẫu và tích hợp hiện có tiếp tục hoạt động, nhưng đưa biểu mẫu về trang Hermes.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 74 test đạt. `git diff --check`: đạt. Snapshot Hermes thật xác nhận gateway đang chạy, job active và đọc được 5 lượt gần đây. Sau khi mở lại server, GET `http://127.0.0.1:5000/hermes` trả HTTP 200.

## Còn lại
Chưa nhấn nút chạy một lượt trên dữ liệu thật vì thao tác này có thể đăng bài đến giờ lên Facebook Page. Chưa commit hoặc push vì yêu cầu hiện tại không đòi hỏi.
