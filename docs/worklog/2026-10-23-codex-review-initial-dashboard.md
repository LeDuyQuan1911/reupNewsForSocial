# Review độc lập initial-dashboard

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Review độc lập diff base `5c78369fcead12bd1356073d80b7a22b0e5b2efd` đến head `61e1753` theo `reviews/requests/initial-dashboard.md`; không sửa implementation, không merge hoặc push. Tập trung `app/`, `run.py`, tests và cấu hình.

## Thực hiện
Đọc quy tắc repo, yêu cầu review, SPEC/README/MAP/PLAN và source ứng dụng. Kiểm tra luồng thu thập, khử trùng, bản nháp, kiểm duyệt, lên lịch, đăng Page. Lưu kết quả tại `reviews/reports/initial-dashboard.md`.

## Quyết định
Giới hạn kiểm tra ở mã ứng dụng; `vendor/` là upstream. Phân loại timeout sau POST là rủi ro P1 do có thể đăng trùng. Không sửa code trong lượt review.

## Kiểm chứng
`node scripts/plugins.mjs check`: hợp lệ. Lệnh unittest tại checkout sạch: 6 lỗi do thiếu `data/`. Chạy từ thư mục tạm có `data/`: 6/6 qua. Kiểm chứng mock timeout: trạng thái thành `failed`, `claim_post` trả true. Đối chiếu checkout chính: `python -m unittest discover -s tests -v` 7/7 qua; `git diff --check` sạch. Chưa kiểm tra dịch vụ thật.

## Còn lại
Đã đối chiếu vòng hai: hai phát hiện được xử lý trong thay đổi chưa commit ở checkout chính; 7/7 test qua. Còn cần kiểm tra với dịch vụ thật và có quy trình thủ công nếu tiến trình dừng ở `publishing`. Đã xác nhận Git status tại checkout sau khi được cấp quyền đọc: chỉ có report và reviewer worklog mới; `git diff --check` sạch. Không có thay đổi implementation.
