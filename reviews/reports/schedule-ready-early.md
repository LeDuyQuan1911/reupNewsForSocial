# Báo cáo review: schedule-ready-early

- Reviewer: Codex reviewer
- Ngày: 2026-10-31
- Base / head: 5babbc7cb288c39b5c382977e5b23c3dc48de377 / 490d99f439372f30323f0192d094261bfa9cae33
- Vòng: độc lập và đối chiếu
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff `app/automation.py`, `tests/test_automation.py`, `PLAN.md`, `contexte/decisions.md`; luồng trạng thái và đặt lịch tại `app/database.py`, luồng đăng trong `app/queue.py`. Không đọc worklog tác giả.
- Lệnh đã chạy và kết quả: head đầu 15/15 test đạt; head cuối `python -m unittest discover -s tests -p test_automation.py -v` — 17/17 đạt. Kịch bản lỗi DB ban đầu được test mới xác nhận đã sửa. Test mới xác nhận kịch bản hẹn bài thủ công đồng thời không còn cộng nhầm.
- Phần chưa kiểm chứng: không gọi model, Facebook Page hoặc đồng hồ thực chạy qua nhiều khung giờ; kiểm tra thời gian dựa trên source và test hiện có. Graph codebase không được dùng vì source liên quan đủ hẹp.

## Phát hiện

### P3 — `scheduled` bị đếm thiếu khi cập nhật job lỗi sau khi hẹn bài

- Vị trí: `app/automation.py:186`
- Điều kiện kích hoạt / cách tái hiện: Một bài đạt kiểm tra; `database.schedule_post` đã lưu trạng thái `scheduled`, sau đó `database.finish_automation_job(..., "scheduled", ...)` tại dòng 168 lỗi một lần.
- Kết quả thực tế: callback bắt lỗi và không cộng kết quả; lượt quét cuối gặp post đã `scheduled`, hoàn tất job theo nhánh dòng 152–154 và trả 0. Kịch bản tái hiện cho `result["scheduled"] == 0` trong khi DB có 1 post `scheduled` và 1 job `scheduled`.
- Kết quả mong đợi: Tổng `scheduled` của lượt phản ánh 1 bài mới hẹn, kể cả khi bước đồng bộ job lỗi tạm thời rồi phục hồi trong cùng lượt.
- Bằng chứng: `schedule_ready` tăng bộ đếm chỉ sau cả hai thao tác DB (dòng 167–170); nhánh phục hồi trạng thái không tăng bộ đếm (dòng 152–154). Chạy kịch bản với `unittest.mock.patch` để `finish_automation_job` ném `OSError` đúng một lần ở trạng thái `scheduled` cho kết quả nêu trên.
- Độ chắc chắn: cao đối với trường hợp lỗi tạm thời đã mô phỏng.
- Hướng sửa gợi ý (nếu có): Theo dõi ID bài được đổi sang `scheduled` trong lượt, hoặc trả số bài đã hẹn từ nhánh phục hồi để tránh đếm thiếu và đếm trùng.


### P3 — Bộ đếm của lượt gồm cả bài đặt lịch thủ công đồng thời

- Vị trí: `app/automation.py:209`
- Điều kiện kích hoạt / cách tái hiện: Trong lúc `run_cycle` chuẩn bị bài, người dùng hẹn một bài thủ công bằng endpoint `/posts/<id>/schedule` của dashboard.
- Kết quả thực tế: Hiệu hai tập `scheduled_post_ids` của toàn DB tính cả bài thủ công; `result["scheduled"]` tăng dù lượt tự động không hẹn bài nào. Kịch bản tái hiện: `prepare_articles` trả 0, thao tác hẹn thủ công diễn ra giữa hai ảnh chụp; kết quả `scheduled=1`, bảng `automation_jobs` rỗng.
- Kết quả mong đợi: `scheduled` của lượt chỉ đếm các bài mà lượt tự động vừa hẹn.
- Bằng chứng: `scheduled_post_ids` trong `app/database.py:1073–1080` lọc mọi bài đăng thật theo trạng thái, không ràng buộc `automation_jobs`; dashboard gọi `database.schedule_post` ở `app/web.py:553`. Khóa `exclusive_cycle` ở `scripts/hermes-automation-job.py` chỉ bảo vệ các lượt cron với nhau, không khóa thao tác dashboard.
- Độ chắc chắn: cao đối với giao thoa thao tác đã tái hiện; khả năng xảy ra phụ thuộc thời điểm người dùng hẹn bài.
- Hướng sửa gợi ý (nếu có): Chỉ chụp ID bài gắn với automation job hoặc theo dõi ID được `schedule_ready` đổi trạng thái trong lượt.

## Đối chiếu sau phản hồi tác giả

Phát hiện P3 ở lượt độc lập đã được sửa tại commit `2d663ff6`: `run_cycle` so ID bài đã hẹn trước/sau lượt, nên trường hợp `finish_automation_job` lỗi một lần vẫn trả `scheduled=1`. Test `test_counts_post_scheduled_before_job_status_retry` xác nhận; rút lại phát hiện này. Phát hiện P3 ở lượt đối chiếu tiếp theo đã được sửa tại commit `490d99f4`: helper chỉ chụp ID bài có `automation_jobs`, loại bài thủ công không gắn job. Test `test_does_not_count_manual_schedule_during_cycle` xác nhận; rút lại phát hiện đó. Không có phát hiện còn mở trong phạm vi review.

## Kết luận cho chủ repo

Hai phát hiện P3 trong các vòng trước đã được sửa và xác nhận bằng test. Không có phát hiện còn mở trong phạm vi diff đã xem; suite automation đạt 17/17. Chưa kiểm chứng tích hợp với model hoặc Facebook. Reviewer không quyết định merge.
