# Báo cáo review: cicd-rollout

- Reviewer: Codex reviewer độc lập
- Ngày: 2026-10-27
- Base / head: `6f578cec842e8db3b6cbc533bdb6bc27809dfc50` / `ac6dac55f5db1b466eada47855d73d3f10f58a62` (head mới thêm `tzdata` so với `2e410a845a60a86450086b06649e31b496a21541`)
- Vòng: độc lập
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: yêu cầu review, `SPEC.md`, `docs/deployment.md`, workflow CI, `scripts/cd/`, runner Hermes, các điểm khởi tạo DB, đăng Page và test liên quan. Diff ứng dụng được kiểm tra; snapshot `vendor/hermes-agent/` không được review toàn bộ vì ngoài phạm vi thay đổi tích hợp.
- Lệnh đã chạy và kết quả: `python -m unittest discover -s tests -q` chạy 95 test nhưng có 2 fail/3 error khi thừa hưởng cấu hình Facebook ở máy review; chạy lại với đúng các biến môi trường rỗng/cờ tắt như CI: 95/95 pass. `python scripts/cd/smoke.py`: pass. PowerShell parser cho hai script CD: pass. `git diff --check` cho phần ngoài vendor và diff bổ sung `tzdata`: pass. Đối chiếu diff `2e410a84..ac6dac55`: chỉ thêm `tzdata>=2024.1` vào `requirements.txt`.
- Phần chưa kiểm chứng: Chưa chạy GitHub Actions hoặc updater/task scheduler trên server Windows thật, chưa gọi Page/9Router. Worktree review ở commit cũ, còn commit head mới chỉ được đọc bằng `git diff`.

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

Chưa thực hiện.

## Kết luận cho chủ repo

Một rủi ro P1 còn lại: rollback sau khi dashboard mới mở có thể xóa dấu vết bài vừa đăng và cho phép đăng trùng. Cần xử lý trước khi cho updater tự chạy trên server. Reviewer không quyết định merge.

