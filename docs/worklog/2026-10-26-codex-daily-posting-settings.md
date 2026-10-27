# Cài số bài và khung giờ đăng, tìm tin mỗi ngày

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cho chủ dự án đặt số bài/ngày và khung giờ đăng; Hermes quét tin tự động một lần mỗi ngày; thêm thao tác quét báo/repo thủ công rõ ràng.

## Thực hiện
Thêm bảng SQLite cho mức bài/ngày, khung giờ và lịch sử đổi mục tiêu; mặc định 6 bài lúc 07:00, 10:00, 13:00, 16:00, 19:00, 22:00. `app/automation.py` đọc cấu hình khi chuẩn bị/xếp lịch và dùng mốc ngày Bangkok để chỉ quét nguồn tự động một lần/ngày. Thêm form ở trang Tài khoản, nút quét báo/repo thủ công, cập nhật tỷ lệ dashboard theo mục tiêu từng ngày. Cập nhật README/MAP/SPEC/PLAN/AGENTS và quyết định dự án.

## Quyết định
Số bài cho phép 1–24/ngày; nhập đúng một giờ cho mỗi bài, các giờ cách nhau ít nhất 30 phút. Cấu hình mới chỉ áp dụng cho bước chuẩn bị và xếp lịch sau khi lưu; bài đã xếp không bị đổi. Mốc mục tiêu lịch sử được lưu riêng để dashboard không dùng mức mới cho ngày cũ. Lượt quét thủ công độc lập với hạn mức quét tự động trong ngày.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 70 bài kiểm tra đạt, gồm ngày Bangkok, lưu/kiểm tra lịch, giới hạn 2 bài, nút quét thủ công và mục tiêu cũ. Dashboard và Tài khoản thực tế trả HTTP 200, form và nút quét hiển thị; dữ liệu hiện tại vẫn là mặc định 6 giờ. Sau khi bật lại Hermes cron, lượt kế tiếp hoàn tất trạng thái `ok` và `hermes cron doctor` không báo lỗi. `git diff --check` và checker worklog được chạy trước bàn giao.

## Còn lại
Hermes cron đã được bật lại sau kiểm tra. Chưa bấm quét nguồn trực tiếp trên dữ liệu thật để tránh tạo bài mới ngoài yêu cầu; route đã được kiểm tra trong test. Máy cần chạy Hermes gateway và 9Router. Không commit/push/merge vì yêu cầu hiện tại chưa đề nghị.
