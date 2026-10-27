# Khắc phục trạng thái Hermes CLI

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Tìm nguyên nhân trang Hermes báo không kết nối được CLI và khắc phục trên máy hiện tại nếu có thể, không làm thay đổi bài đăng hoặc lịch.

## Thực hiện
Đối chiếu `/hermes/status`, Hermes CLI và trạng thái cron: CLI có trên máy, nhưng gateway nền đã dừng và scheduler báo bỏ lỡ khoảng 11 giờ. Gọi `hermes gateway ensure --timeout 60`, khởi động lại tiến trình dashboard đang dùng môi trường cũ. Trang sau đó nhận gateway và job đang chạy. Sửa `scripts/start-local-services.ps1` để đợi 9Router sẵn sàng rồi bảo đảm gateway chạy khi repo có marker Hermes; cập nhật README, MAP, PLAN và quyết định kỹ thuật. Không sửa bài đăng hoặc lịch. Sau khi gateway phục hồi, runner đã xử lý ba bài quá giờ; SQLite ghi cả ba ở trạng thái đã đăng.

## Quyết định
Giữ Hermes cron là bộ chạy lịch; script mở dịch vụ chỉ khởi động gateway khi repo đã giao quyền điều phối cho Hermes. Đợi 9Router trước vì job chạy bù có thể cần model kiểm duyệt. Không tự thay đổi quy tắc xử lý bài quá giờ trong nhiệm vụ này.

## Kiểm chứng
`hermes cron status` xác nhận gateway và một job active. `/hermes/status` trả HTTP 200 với `gateway=true`, `job=active`, không còn lỗi; chạy lại script cũng giữ trạng thái tốt. PowerShell parser không báo lỗi. `git diff --check` và `node scripts/check-worklog.mjs` đạt.

## Còn lại
Gateway đã dừng giữa phiên dù mục tự khởi động khi đăng nhập Windows vẫn tồn tại; script mới khắc phục khi chạy lại hoặc ở lần đăng nhập sau, nhưng chưa có giám sát liên tục để tự phục hồi nếu gateway dừng giữa phiên. Ba bài quá giờ đã được gửi muộn sau khi gateway chạy lại; cần người dùng kiểm tra trên Page nếu muốn đối chiếu nội dung thực tế.
