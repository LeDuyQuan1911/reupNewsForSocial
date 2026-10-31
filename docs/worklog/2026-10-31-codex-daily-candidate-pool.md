# Nhóm ứng viên 25–30 tin mỗi ngày

- Ngày: 2026-10-31
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Với lịch 19 bài/ngày, tìm khoảng 25–30 tin mới để có bài dư thay tin bị chặn, giữ giờ đăng đã cấu hình và kiểm duyệt trước đăng.

## Thực hiện
Nâng giới hạn đề xuất web Hermes từ 24 lên 30 URL trong `app/hermes_research.py`. Thêm giới hạn tối đa 30 ứng viên tự động khác nhau/ngày trong `app/database.py`; bài giữ lịch 00:00 từ tối hôm trước cũng được tính vào giới hạn của ngày mới. Thêm test trong `tests/test_automation.py` và `tests/test_hermes_research.py`. Cập nhật `README.md`, `SPEC.md`, `PLAN.md` và `contexte/decisions.md`. Không đổi dữ liệu server hoặc secrets.

## Quyết định
Phân biệt tin thô RSS/GitHub được lưu với ứng viên mà luồng tự động chọn để soạn: giới hạn 30 áp dụng cho ứng viên được thử, còn tin thô có thể nhiều hơn. Đây là giới hạn chi phí và nguồn dự phòng, không hứa 30 URL đều hợp lệ hoặc 19 bài đều đạt kiểm duyệt.

## Kiểm chứng
`python -m unittest discover -s tests -p test_automation.py -q`: 24 test đạt. `python -m unittest discover -s tests -p test_hermes_research.py -q`: 8 test đạt. `git diff --check`: sạch. Review độc lập tại `C:\Users\PC\Desktop\reupNewsForSocial-refill-review\reviews\reports\candidate-pool-30-independent.md` không có phát hiện đã xác nhận.

## Còn lại
Chưa triển khai lên server; PR/push/merge chưa được yêu cầu. Nếu người dùng muốn giới hạn luôn số tin thô lưu từ RSS/GitHub, cần thay đổi riêng cơ chế thu thập nguồn và phân bổ số suất theo từng nguồn.
