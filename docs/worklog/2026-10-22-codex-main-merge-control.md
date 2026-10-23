# Chỉ chủ dự án được merge vào main

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi

Thiết lập repository GitHub để các thành viên khác vẫn tạo pull request nhưng chỉ chủ dự án quyết định merge vào nhánh `main`.

## Thực hiện

Kiểm tra repository GitHub và xác nhận `main` là nhánh mặc định, repo công khai, chưa có ruleset hoặc branch protection và chỉ chủ repo có quyền collaborator. Tạo `governance/github-main-ruleset.json` cùng hướng dẫn trong `governance/README.md`; áp dụng [ruleset #25650325](https://github.com/LeDuyQuan1911/setupSourceVibeCode/rules/25650325) trên GitHub. Cập nhật `AGENTS.md`, `MULTI_AGENT.md`, `MAP.md`, `PLAN.md` và README.

## Quyết định

Chỉ tài khoản `LeDuyQuan1911` được bypass quy tắc cập nhật `main` khi merge qua PR. Mọi thành viên khác vẫn có thể đề xuất PR từ branch hoặc fork, nhưng không có quyền cập nhật `main`. Giữ quyền admin cho chủ repo.

## Kiểm chứng

Đọc lại ruleset từ GitHub: enforcement `active`, áp dụng `refs/heads/main`, bypass actor đúng user ID 117301665 ở chế độ `pull_request`; các quy tắc hiệu lực gồm `update`, `deletion`, `non_fast_forward`, `pull_request`. Repo vẫn cho phép fork và không bật auto merge. Kiểm tra JSON và `git diff --check`.

## Còn lại

Chưa thử bằng tài khoản thành viên thứ hai vì hiện chưa có collaborator khác. Nếu sau này cấp quyền admin cho người khác, họ có thể sửa hoặc xóa ruleset.
