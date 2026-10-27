# Báo cáo review: cicd-rollout

- Reviewer: Codex reviewer độc lập
- Ngày: 2026-10-27
- Base / head: `6f578cec842e8db3b6cbc533bdb6bc27809dfc50` / `ceb842d9fb03cf1645effd3e1740acaf1a57eb7b` (lượt đầu kết thúc tại `ac6dac55f5db1b466eada47855d73d3f10f58a62`)
- Vòng: đối chiếu
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: yêu cầu review, `SPEC.md`, `docs/deployment.md`, workflow CI, `scripts/cd/`, runner Hermes, các điểm khởi tạo DB, đăng Page và test liên quan. Diff ứng dụng được kiểm tra; snapshot `vendor/hermes-agent/` không được review toàn bộ vì ngoài phạm vi thay đổi tích hợp.
- Lệnh đã chạy và kết quả: `python -m unittest discover -s tests -q` chạy 95 test nhưng có 2 fail/3 error khi thừa hưởng cấu hình Facebook ở máy review; chạy lại với đúng các biến môi trường rỗng/cờ tắt như CI: 95/95 pass. `python scripts/cd/smoke.py`: pass. PowerShell parser cho hai script CD: pass. `git diff --check` cho phần ngoài vendor và diff bổ sung `tzdata`: pass. Đối chiếu diff `2e410a84..ac6dac55`: chỉ thêm `tzdata>=2024.1` vào `requirements.txt`.
- Phần chưa kiểm chứng: Chưa chạy GitHub Actions hoặc updater/task scheduler trên server Windows thật, chưa gọi Page/9Router. Head đối chiếu đã được checkout tạm để chạy test rồi trả lại branch review.

## Phát hiện

### P1 — Rollback có thể xóa trạng thái bài đã đăng trong lúc dashboard mới đang phục vụ

- Vị trí: `scripts/cd/update-server.ps1:148` và `scripts/cd/update-server.ps1:163`
- Điều kiện kích hoạt / cách tái hiện: Updater đã sao lưu DB ở dòng 138 và khởi động dashboard mới ở dòng 148. Trong khoảng đó, người dùng bấm “Đăng ngay” trên dashboard; sau khi Meta nhận bài, bước sao chép runner hoặc `hermes cron resume` ở dòng 149–151 lỗi.
- Kết quả thực tế: Route `/posts/<id>/publish` vẫn cho phép `queue.process_claimed_post` gửi bài lên Page (`app/web.py:544–558`), vì cờ `deployment-paused` chỉ được runner Hermes kiểm tra (`scripts/hermes-automation-job.py:101–107`). Nhánh rollback ở dòng 163 ghi đè DB bằng bản sao trước lúc đăng, làm mất `platform_post_id`, trạng thái `published` và trạng thái bình luận. Bài trên Facebook vẫn tồn tại; DB cũ có thể cho đăng lại, dẫn đến bài trùng. Các thao tác sửa nháp/cấu hình trong cửa sổ này cũng bị mất.
- Kết quả mong đợi: Không có thao tác ghi hoặc gửi bài qua web trong toàn bộ khoảng có thể rollback; hoặc rollback giữ mọi thay đổi đã xác nhận sau bản backup và không đưa bài đã gửi trở lại trạng thái có thể đăng.
- Bằng chứng: Thứ tự backup → `Start-OwnedDashboard` → resume trong `update-server.ps1:138–153`; rollback DB ở dòng 163; route đăng trực tiếp ở `app/web.py:544–558`; chỉ runner kiểm tra marker ở `scripts/hermes-automation-job.py:101–107`.
- Độ chắc chắn: cao.
- Hướng sửa gợi ý: Giữ dashboard không phục vụ các POST có tác dụng trong lúc deploy có thể rollback, hoặc chỉ mở dashboard sau khi các bước có thể lỗi đã hoàn tất; bổ sung cơ chế phục hồi bảo toàn trạng thái đăng nếu lỗi sau khi mở phục vụ.

## Đối chiếu sau phản hồi tác giả

- **Phát hiện P1 được sửa tại `ceb842d9`.** `app/web.py:25–31` trả 503 cho mọi request ngoài `/healthz` khi có `data/deployment-paused`; updater gọi `/healthz` để kiểm tra dashboard. Test mới xác nhận GET `/`, POST và health check khi marker tồn tại. Trước lúc gọi `hermes cron resume`, web không thể gửi Page hoặc ghi DB qua route; nếu đã thử resume mà có lỗi, updater giữ marker và không tự phục hồi DB (`scripts/cd/update-server.ps1:150–163`). Do đó chuỗi gây mất trạng thái bài đăng trong phát hiện ban đầu không còn xảy ra theo code hiện tại.
- Kiểm tra độc lập trên head `ceb842d9`: 96/96 test pass với biến môi trường CI; smoke pass; cú pháp PowerShell pass; `git diff --check ac6dac55..ceb842d9` pass. Không thấy P1 mới trong diff đối chiếu.

## Kết luận cho chủ repo

Phát hiện P1 ban đầu đã được sửa trong diff đối chiếu. Chưa kiểm chứng hành vi updater/task scheduler và Page trên server Windows thật; lỗi sau khi thử resume cần đối chiếu thủ công theo thiết kế. Reviewer không quyết định merge.
