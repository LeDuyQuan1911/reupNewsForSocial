# Báo cáo review: candidate-pool-30

- Reviewer: Codex reviewer độc lập
- Ngày: 2026-10-31
- Base / head: `dcd6a6b69bbba76ed4cec5eadb4a13c48ad53e78` / cùng HEAD, diff chưa commit
- Vòng: độc lập
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff mới trong `app/database.py`, `app/hermes_research.py`, `tests/test_automation.py`, `tests/test_hermes_research.py`, `README.md`, `SPEC.md`, `contexte/decisions.md`; đối chiếu thêm `app/automation.py` và hàm `find_articles()` để xác nhận cách dùng giới hạn 30. Không đọc worklog của tác giả trước báo cáo này.
- Lệnh đã chạy và kết quả: `python -m unittest discover -s tests -p test_automation.py`: 24 test đạt; `python -m unittest discover -s tests -p test_hermes_research.py`: 8 test đạt; `git diff --check`: không báo lỗi whitespace.
- Phần chưa kiểm chứng: chưa gọi Hermes, nguồn web, model hoặc Facebook thật. Test giới hạn 30 dựng trực tiếp các job trong SQLite; chưa chạy luồng từ 30 URL đến 30 lần chuẩn bị ảnh/nội dung qua model thật.

## Phát hiện

Không có phát hiện sau phạm vi kiểm tra nêu trên.

## Đối chiếu sau phản hồi tác giả

Chưa thực hiện.

## Kết luận cho chủ repo

Với mục tiêu 19, prompt Hermes dùng giới hạn 30 URL. Truy vấn claim và quyết định quét bù dùng cùng giới hạn 30 ứng viên/ngày Bangkok, kể cả bài giữ chỗ 00:00 từ hôm trước; bài bị blocked vẫn nhường suất đăng nhưng không mở thêm lượt claim thứ 31. Cổng kiểm duyệt, giờ đăng và quota trong `app/automation.py` không đổi ở phần diff mới. Reviewer không quyết định merge.
