# Review độc lập cicd-rollout

- Ngày: 2026-10-27
- Agent: Codex reviewer
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Review độc lập diff từ `6f578cec842e8db3b6cbc533bdb6bc27809dfc50` đến head đối chiếu `ceb842d9fb03cf1645effd3e1740acaf1a57eb7b`, tập trung CI/CD, an toàn dữ liệu và tích hợp ứng dụng. Chỉ sửa report và worklog; commit request đã có.

## Thực hiện
Đọc yêu cầu review, quy trình, source CI/CD và các điểm tích hợp web/Hermes; ghi một phát hiện P1 về rollback có thể làm mất dấu vết bài đã đăng tại `reviews/reports/cicd-rollout.md`. Đọc diff bổ sung `tzdata` ở head trước và diff sửa lỗi `ac6dac55..ceb842d9`; cập nhật phần đối chiếu trong report, xác nhận P1 đã được sửa.

## Quyết định
Giữ nguyên phát hiện lượt độc lập làm lịch sử; phần đối chiếu ghi rõ bằng chứng sửa. Không sửa implementation.

## Kiểm chứng
95 test fail 2/error 3 khi thừa hưởng cấu hình Facebook riêng của máy review; với đúng biến môi trường CI: 95/95 pass. Smoke dashboard pass. Hai script CD parse PowerShell pass. Diff check phần ngoài vendor, diff bổ sung `tzdata` và diff sửa P1 pass. Trên head `ceb842d9`, 96/96 test với env CI pass, smoke pass, script updater parse PowerShell pass.

## Còn lại
Chưa chạy workflow GitHub Actions hoặc updater/task scheduler trên server Windows thật; chưa thử Page/9Router. P1 ban đầu đã được sửa qua đối chiếu; chưa kiểm chứng deploy thật và kịch bản lỗi Task Scheduler/Hermes trên server.
