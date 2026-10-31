# Báo cáo review: refill-blocked

- Reviewer: Codex reviewer độc lập
- Ngày: 2026-10-31
- Base / head: `dcd6a6b69bbba76ed4cec5eadb4a13c48ad53e78` / cùng HEAD, diff chưa commit
- Vòng: đối chiếu (sau báo cáo độc lập)
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff trong `app/automation.py`, `app/database.py`, `tests/test_automation.py`, `README.md`, `SPEC.md`, `contexte/decisions.md`; đối chiếu thêm `app/queue.py`, các hàm lịch đăng và quota trong database.
- Lệnh đã chạy và kết quả: `python -m unittest discover -s tests -p test_automation.py`: 23 test đạt sau bản sửa; `git diff --check` không có lỗi whitespace. `python -m unittest tests.test_automation` không nạp được module vì `tests` không là package; dùng lệnh discover thay thế.
- Phần chưa kiểm chứng: không gọi model, nguồn tin hoặc Facebook thật.

## Phát hiện

### P1 — Bài còn `ready` từ ngày trước được xếp lịch sang ngày mới

- Vị trí: `app/automation.py:155`, `app/automation.py:172-176`
- Điều kiện kích hoạt / cách tái hiện: cấu hình 1 bài/ngày lúc 08:00. Một bài được chuẩn bị và chuyển `ready` sau 08:00 ngày D (ví dụ máy bật lại lúc 09:00); trong ngày D không còn giờ phù hợp. Gọi lại `schedule_ready()` trước 08:00 ngày D+1.
- Kết quả thực tế: lượt ngày D không xếp bài vì `next_slot()` trả 08:00 ngày D+1 và hàm kiểm tra ngày từ chối. Nhưng `ready_automation_jobs()` vẫn trả job đó ở ngày D+1; lúc này `slot_is_for_current_day_or_next_midnight()` nhận 08:00 là ngày hiện tại và bài được xếp lịch. Bài của ngày D do đó bị chuyển sang ngày sau dù không thuộc ngoại lệ 00:00.
- Kết quả mong đợi: job `ready` từ ngày D chỉ được xếp vào giờ còn lại của D, ngoại trừ 00:00 ngày D+1 được chuẩn bị sau giờ cuối của D; nếu lỡ giờ thì giữ để xử lý hoặc kết thúc job, không tự xếp vào ngày sau.
- Bằng chứng: `ready_automation_jobs()` trong `app/database.py:1122-1132` không lọc ngày `claimed_at`. `schedule_ready()` ở `app/automation.py:155-176` chỉ so slot với *thời điểm gọi hiện tại*, không so với ngày job được tạo. `tests/test_automation.py:224-239` chỉ gọi một lần cùng ngày nên không bắt được lượt ngày kế tiếp.
- Độ chắc chắn: cao.
- Hướng sửa gợi ý: ràng buộc ngày của job và ngày slot, giữ ngoại lệ 00:00 có điều kiện; thêm test chạy `schedule_ready()` ở cả ngày D và D+1.

## Đối chiếu sau phản hồi tác giả

Phát hiện P1 đã được sửa: `app/automation.py:159-163` đánh dấu failed cho job `ready` được claim trước ngày Bangkok hiện tại, tránh xếp vào slot hôm nay. `tests/test_automation.py:241-258` xác nhận trường hợp bài cũ từ hôm qua không lấy slot 08:00 hôm nay. Trong lúc đối chiếu, phát hiện guard mới ban đầu chạy trước nhánh khôi phục post đã có lịch; tác giả đã chuyển nhánh khôi phục lên `app/automation.py:156-158` và thêm test ở `tests/test_automation.py:260-276`. Test 23/23 đạt. Không còn phát hiện đã xác nhận trong phạm vi này.

## Kết luận cho chủ repo

Phát hiện P1 của vòng độc lập đã được xử lý và kiểm chứng bằng test qua ranh giới ngày. Chưa kiểm chứng tích hợp với model, nguồn tin và Facebook thật; reviewer không quyết định merge.
