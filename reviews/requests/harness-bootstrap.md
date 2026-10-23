# Yêu cầu review: harness-bootstrap

- Base commit: d4d15b3a5dcce8964ad83deac64a0d2a4a851189
- Head commit hoặc PR: 9c9b8bad70fd3a19632c211e1d2e3327f9d8bd44
- Phạm vi file:
  - .gitignore
  - AGENTS.md
  - CLAUDE.md
  - MAP.md
  - MULTI_AGENT.md
  - PLAN.md
  - README.md
  - SPEC.md
  - contexte/decisions.md
  - docs/worklog/2026-10-22-codex-independent-review.md
  - docs/worklog/2026-10-22-codex-main-merge-control.md
  - docs/worklog/2026-10-22-codex-multi-agent.md
  - docs/worklog/2026-10-22-codex-plugin-catalog.md
  - docs/worklog/2026-10-22-codex-repo-foundation.md
  - docs/worklog/2026-10-22-codex-worklog-policy.md
  - docs/worklog/README.md
  - governance/README.md
  - governance/github-main-ruleset.json
  - livrables/README.md
  - plugins/README.md
  - plugins/ci-cd/INSTRUCTIONS.md
  - plugins/ci-cd/plugin.json
  - plugins/documentation/INSTRUCTIONS.md
  - plugins/documentation/plugin.json
  - plugins/independent-review/INSTRUCTIONS.md
  - plugins/independent-review/plugin.json
  - plugins/prototype/INSTRUCTIONS.md
  - plugins/prototype/plugin.json
  - plugins/security/INSTRUCTIONS.md
  - plugins/security/plugin.json
  - plugins/testing/INSTRUCTIONS.md
  - plugins/testing/plugin.json
  - project.plugins.json
  - reviews/README.md
  - reviews/templates/REPORT.md
  - reviews/templates/REQUEST.md
  - scripts/check-worklog.mjs
  - scripts/plugins.mjs
  - scripts/review-brief.mjs
- Tiêu chí chấp nhận: Codex, Antigravity và Claude dùng một bộ quy tắc repo; plugin có thể bật/tắt và chỉ plugin bật có hiệu lực; mỗi nhiệm vụ có worklog kiểm tra được; yêu cầu review có base/head rõ; tài liệu phản ánh đúng repo chưa có source ứng dụng; quy trình không cho agent tự quyết định merge vào `main`.
- Lệnh kiểm tra khả dụng: `node scripts/plugins.mjs check`; `node scripts/check-worklog.mjs --all` (bỏ qua worklog của phiên merge còn đang làm); `node --check scripts/plugins.mjs`, `node --check scripts/check-worklog.mjs`, `node --check scripts/review-brief.mjs`; `git diff --check main...HEAD`.
- Ngoài phạm vi: code ứng dụng, triển khai CI/CD, cài MCP hoặc cấu hình môi trường production.

## Prompt cho reviewer

Hãy review độc lập thay đổi giữa base và head. Đọc `AGENTS.md`, plugin `independent-review`, `reviews/README.md` và yêu cầu này. Dùng phiên/ngữ cảnh riêng; ở lượt đầu chưa đọc giải thích hoặc kết luận của tác giả. Xem diff và code liên quan, kiểm tra hành vi theo tiêu chí chấp nhận. Không sửa implementation. Ghi báo cáo theo `reviews/templates/REPORT.md`, nêu bằng chứng cụ thể hoặc nói rõ không có phát hiện. Tạo worklog riêng cho nhiệm vụ review.
