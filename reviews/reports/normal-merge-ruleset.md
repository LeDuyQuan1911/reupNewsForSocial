# Báo cáo review: normal-merge-ruleset

- Reviewer: Codex (reviewer độc lập)
- Ngày: 2026-10-22
- Base / head: a9b284aee1b3a1f8c58228ecdb4d3dba4b27e0b0 / working tree chưa commit
- Vòng: độc lập
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff `HEAD` của `governance/github-main-ruleset.json`, `governance/README.md`, `contexte/decisions.md`; cấu hình ruleset và quyền repo hiện hành trên GitHub. Không đọc worklog tác giả hoặc giải thích của tác giả trước kết luận này.
- Lệnh đã chạy và kết quả: kiểm tra JSON bằng Node đạt (active, branch `main`, không có `update`/bypass, có `deletion`, `non_fast_forward`, `pull_request`); `git diff --check HEAD --` cho ba file đạt. GitHub API ruleset #25650325 trả active, không có bypass, và đúng ba rule trên; API effective rules của `main` trả cùng ba rule. API branch protection cổ điển trả 404 `Branch not protected`. API repo trả public, `allow_forking=true`, owner là tài khoản User `LeDuyQuan1911`; API collaborators chỉ liệt kê tài khoản này với quyền Admin/Push.
- Phần chưa kiểm chứng: chưa dùng nút Merge trên một PR thật; chưa kiểm tra mọi policy ngoài ruleset có thể ảnh hưởng PR cụ thể. Quyền collaborator là trạng thái có thể thay đổi sau thời điểm truy vấn.

## Phát hiện

Không có phát hiện sau phạm vi kiểm tra nêu trên. Theo [GitHub Docs về ruleset](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), bỏ `Restrict updates` trong khi giữ `Require a pull request`, `Block force pushes` và `Restrict deletions` phù hợp mục tiêu cấu hình. [GitHub Docs về repo cá nhân](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository) xác nhận collaborator có quyền write, nên giới hạn người có thể merge hiện phụ thuộc danh sách collaborator đã kiểm tra.

## Đối chiếu sau phản hồi tác giả

Chưa thực hiện.

## Kết luận cho chủ repo

Cấu hình working tree và ruleset đang chạy phù hợp tiêu chí review tại thời điểm kiểm tra. Cần duy trì chỉ chủ repo có quyền Write/Admin nếu muốn độc quyền merge. Việc nhấn Merge trên một PR thật vẫn là phần chưa kiểm chứng. Reviewer không quyết định merge.
