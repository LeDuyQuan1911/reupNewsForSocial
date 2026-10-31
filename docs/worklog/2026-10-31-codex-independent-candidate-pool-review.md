# Review độc lập giới hạn 30 ứng viên tự động

- Ngày: 2026-10-31
- Agent: Codex reviewer độc lập
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Review chỉ đọc diff mới về Hermes đề xuất tối đa 30 URL khi mục tiêu 19 bài/ngày và automation claim tối đa 30 tin khác nhau/ngày. Đối chiếu các cổng quota, kiểm duyệt, lịch đăng, test và tài liệu; không sửa implementation và không đọc worklog tác giả trước báo cáo đầu tiên.

## Thực hiện
Đã đối chiếu diff với luồng Hermes đề xuất URL, claim ứng viên, giới hạn 30 qua ngày Bangkok và trường hợp giữ chỗ 00:00. Ghi report tại `reviews/reports/candidate-pool-30-independent.md`. Không sửa implementation và không đọc worklog tác giả trước báo cáo.

## Quyết định
Không có phát hiện đã xác nhận. Giữ giới hạn 30 trên số tin được claim, gồm ứng viên giữ chỗ 00:00 từ hôm trước; bài blocked không tính vào suất đăng nhưng vẫn thuộc 30 tin đã thử.

## Kiểm chứng
`python -m unittest discover -s tests -p test_automation.py`: 24 test đạt. `python -m unittest discover -s tests -p test_hermes_research.py`: 8 test đạt. `git diff --check`: không có lỗi whitespace. Không kiểm tra tích hợp dịch vụ thật.

## Còn lại
Chưa kiểm chứng Hermes, nguồn web, model hoặc Facebook thật. Không có bước tiếp theo bắt buộc trong phạm vi review này.
