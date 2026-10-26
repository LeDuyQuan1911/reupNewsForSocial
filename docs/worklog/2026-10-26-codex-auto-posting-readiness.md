# Điều kiện đăng bài tự động

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Xác định những gì còn cần để hệ thống hiện tại tự đăng bài, phân biệt Facebook Page và nhóm.

## Thực hiện
Đọc `run.py`, `app/automation.py`, `app/queue.py`, `app/facebook.py`, `.env.example` và nhật ký thiết lập đăng nhóm trước đó. Kiểm tra chỉ trạng thái có/không của biến môi trường, cổng localhost và Task Scheduler; tra tài liệu Meta về Page và Groups. Không đăng bài hay truy cập tài khoản Facebook. Chỉ thêm nhật ký này.

## Quyết định
Phân biệt hai đích: luồng tự động hiện có chỉ đăng Facebook Page qua Graph API; Hermes chưa nối vào luồng này. Đăng nhóm cần một tích hợp riêng qua trình duyệt hoặc cách được Meta hỗ trợ tại thời điểm triển khai, không suy ra từ việc đã cài Hermes.

## Kiểm chứng
`REUP_AUTO_ENABLED=1`; model text/vision và key tồn tại; cổng 5000/20128 mở; tác vụ đăng nhập Windows tồn tại. `REUP_FACEBOOK_PAGE_ID`, `REUP_FACEBOOK_PAGE_TOKEN`, `REUP_META_GRAPH_VERSION` đều chưa đặt. Source xác nhận chuẩn bị tối đa 6 bài/ngày, đặt các khung giờ Bangkok khi Page sẵn sàng và gửi qua `/photos`/`/feed`. Trang Meta trực tiếp bị HTTP 429 qua công cụ web, nên không xác nhận tại chỗ chi tiết quyền/token phiên bản mới nhất.

## Còn lại
Để Page đăng thật: người dùng cần chọn Page, cấu hình Meta App/Page token có quyền phù hợp, đặt ba biến còn thiếu trên máy, khởi động lại dịch vụ và thử một bài. Để đăng nhóm: cần nhóm đích, tài khoản/Page có quyền đăng và xây thêm luồng browser; chưa có adapter nhóm. Máy phải bật, đăng nhập và các dịch vụ phải chạy khi đến giờ.
