# Quyền merge vào main

Repo triển khai: `LeDuyQuan1911/reupNewsForSocial`. File `github-main-ruleset.json` ghi cấu hình mong muốn cho ruleset nhánh `main`, gồm PR và check `Python tests (Windows)` chạy trên mã mới nhất của `main`.

Ruleset từ `setupSourceVibeCode` chỉ là nguồn mẫu. Ngày 2026-10-27, [ruleset #25950396](https://github.com/LeDuyQuan1911/reupNewsForSocial/rules/25950396) đã được bật trên GitHub cho `reupNewsForSocial` sau lượt CI đầu tiên; xem [`docs/deployment.md`](../docs/deployment.md).

- Người đóng góp fork repo công khai và mở PR vào `main`; họ không cần quyền Write trên repo gốc.
- Cấu hình mong muốn yêu cầu PR và check CI mới nhất, chặn force push và xóa `main`. Chủ repo merge bằng nút thường sau khi đáp ứng yêu cầu.
- Chỉ tài khoản GitHub `LeDuyQuan1911` có quyền Write/Admin trên repo gốc và quyết định merge. Giới hạn người merge đến từ quyền truy cập repo, không phải ruleset.
- Quyền merge là quyền của tài khoản GitHub, không phụ thuộc agent nào tạo PR. Agent chỉ merge khi chủ repo yêu cầu rõ đối với PR cụ thể.

Repo thuộc tài khoản cá nhân nên collaborator được cấp quyền Write; mời thêm collaborator sẽ cho họ khả năng merge PR. Muốn thành viên push branch trực tiếp vào repo gốc nhưng không được merge `main`, cần chuyển sang repository thuộc organization với quyền nhánh phù hợp hoặc dùng lại cơ chế bypass. Người có quyền Admin khác cũng có thể sửa ruleset. Kiểm tra danh sách quyền truy cập mỗi khi mời người mới.

Kiểm tra trạng thái ruleset trên GitHub tại trang Settings → Rules → Rulesets hoặc bằng `gh api repos/LeDuyQuan1911/reupNewsForSocial/rulesets`. Cấu hình trong file này không tự đồng bộ khi chỉnh file; thay đổi GitHub phải được áp dụng riêng và ghi vào worklog.
