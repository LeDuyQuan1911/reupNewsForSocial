# Chỉnh ruleset để merge không bypass

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Đổi bảo vệ `main` để chủ repo có thể merge PR bằng nút thường; người khác vẫn có thể mở PR nhưng không có quyền merge. Không merge PR #2.

## Thực hiện
Kiểm tra repo công khai, ruleset thực tế và danh sách cộng tác viên. Phát hiện `nvlinh230893` có quyền Write; xác nhận không có fork hoặc PR đang mở của tài khoản này rồi rút quyền collaborator. Sau đó cập nhật ruleset #25650325: bỏ `update` và bypass actor, giữ `pull_request`, `deletion`, `non_fast_forward`. Cập nhật `governance/github-main-ruleset.json`, `governance/README.md` và `contexte/decisions.md`.

## Quyết định
Giữ yêu cầu pull request và chặn xóa, force push `main`. Quyền merge độc quyền dựa vào việc chỉ chủ repo còn quyền Write/Admin; người khác dùng fork vì đây là repo công khai thuộc tài khoản cá nhân. Không merge PR #2.

## Kiểm chứng
GitHub API xác nhận repo công khai; trước thay đổi có owner và `nvlinh230893` (Write). Rút collaborator trả HTTP 204; đọc lại chỉ còn `LeDuyQuan1911:admin`, không có lời mời collaborator đang chờ. Lần cập nhật ruleset đầu dùng PATCH trả 404 và không làm đổi cấu hình; dùng PUT theo tài liệu GitHub thành công. Đọc lại ruleset đang `active`, bypass list rỗng; endpoint effective rules của `main` chỉ trả `deletion`, `non_fast_forward`, `pull_request`. PR #2 còn `open`, `mergeable=true`, `mergeable_state=clean`. JSON cục bộ parse được, manifest plugin hợp lệ, `git diff --check` không báo lỗi nội dung. Reviewer độc lập ghi `reviews/reports/normal-merge-ruleset.md`, không có phát hiện; xác nhận repo cho phép fork và chỉ owner có Admin/Push.

## Còn lại
Chưa kiểm tra giao diện nút Merge bằng tài khoản chủ repo; API xác nhận cấu hình và PR có thể merge. PR #2 chưa được merge. Hai worklog không theo dõi của nhiệm vụ PR khác được giữ nguyên.
