# Review độc lập cicd-rollout

- Ngày: 2026-10-27
- Agent: Codex reviewer
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Review độc lập diff từ `6f578cec842e8db3b6cbc533bdb6bc27809dfc50` đến head `ac6dac55f5db1b466eada47855d73d3f10f58a62`, tập trung CI/CD, an toàn dữ liệu và tích hợp ứng dụng. Chỉ sửa report và worklog; commit request đã có.

## Thực hiện
Đọc yêu cầu review, quy trình, source CI/CD và các điểm tích hợp web/Hermes; ghi một phát hiện P1 về rollback có thể làm mất dấu vết bài đã đăng tại `reviews/reports/cicd-rollout.md`. Đọc diff bổ sung `tzdata` ở head mới.

## Quyết định
Giữ report trong lượt độc lập và chỉ nêu lỗi có chuỗi điều kiện/bằng chứng cụ thể. Không sửa implementation.

## Kiểm chứng
95 test fail 2/error 3 khi thừa hưởng cấu hình Facebook riêng của máy review; với đúng biến môi trường CI: 95/95 pass. Smoke dashboard pass. Hai script CD parse PowerShell pass. Diff check phần ngoài vendor và diff bổ sung `tzdata` pass.

## Còn lại
Chưa chạy workflow GitHub Actions hoặc updater/task scheduler trên server Windows thật; chưa thử Page/9Router. Cần tác giả xử lý phát hiện P1 và reviewer đối chiếu sau phản hồi.
