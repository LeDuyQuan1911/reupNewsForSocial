# Chuyển điều phối tự động sang Hermes

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cho Hermes vận hành luồng tự động của ứng dụng về sau, thay các thread nền trong dashboard; giữ giới hạn và kiểm tra trước khi đăng Facebook Page. Cấu hình có thể dựng lại khi mang repo sang máy khác.

## Thực hiện
Xác định `run.py` từng tạo hai thread quét và xử lý bài đến giờ; Hermes gateway có cron riêng. Thêm `scripts/hermes-automation-job.py` để Hermes cron gọi các hàm hiện có, đọc cấu hình User và ghi thời điểm chạy. Thêm `scripts/install-hermes-automation.ps1` chép runner vào Hermes scripts, cài gateway tự mở khi đăng nhập và tạo job mỗi phút. `run.py` dừng tạo thread khi marker Hermes tồn tại. Trang Tài khoản hiển thị bộ chạy và lần chạy gần nhất. Cập nhật README/MAP/SPEC/PLAN/AGENTS/quyết định dự án.

## Quyết định
Dùng job Hermes `no-agent` cho nhịp một phút để không tốn token lúc không có bài mới; khi cần viết, runner gọi Hermes CLI thật theo brief biên tập. Các thao tác nguồn/ảnh/kiểm duyệt/đăng tiếp tục qua code có điều kiện an toàn và 9Router. Job xử lý bài đến giờ ngay cả khi tắt riêng chức năng tìm tin tự động. Có khóa file tránh hai lượt cron chạy chồng nhau. Không đặt secret hay dữ liệu Hermes vào Git.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 66 test đạt. `node scripts/plugins.mjs check` và `git diff --check` đạt. Chạy installer hai lần: tạo rồi cập nhật cùng một Hermes job; gateway có mục tự mở khi đăng nhập. Trang Tài khoản HTTP 200 hiển thị Hermes quản lý lịch. Đã đóng dashboard và quan sát Hermes tự kích hoạt rồi hoàn tất lượt cron mới: trạng thái `ok`, chuẩn bị 2 bài và xếp lịch 2 bài, không có cron incident. Sau đó mở dashboard lại.

## Còn lại
Máy phải bật/đăng nhập Windows và 9Router phải sẵn sàng; Hermes gateway đang dùng mục Startup theo người dùng vì Windows Scheduled Task cần quyền quản trị. Hermes là bộ điều phối lịch và người viết nháp; quyết định chọn tin/ảnh và kiểm duyệt vẫn dùng code ứng dụng cùng model 9Router, không thay bằng prompt tự do. Hai bài vừa xếp lịch chưa được kiểm chứng đăng thành công trên Page. Không commit/push/merge vì yêu cầu hiện tại chưa đề nghị.
