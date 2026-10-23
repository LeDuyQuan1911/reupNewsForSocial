# Làm việc với Codex, Antigravity và Claude Code

## Một nguồn quy tắc

- `AGENTS.md` là quy tắc chung cho cả ba công cụ. Antigravity và Codex đọc file này trong workspace; `CLAUDE.md` import file này cho Claude Code.
- `SPEC.md` mô tả điều cần xây; `MAP.md` chỉ vị trí source; `PLAN.md` giữ kế hoạch chung; `contexte/decisions.md` lưu quyết định đã chốt; `docs/worklog/` ghi từng nhiệm vụ.
- Không chép nguyên bộ quy tắc sang `GEMINI.md`, `.agents/rules/` hay `.claude/rules/`. Chỉ thêm rule riêng khi một công cụ thực sự cần hành vi khác.

## Chia việc

Một người điều phối (có thể là bạn hoặc một agent được giao) chia việc thành các nhiệm vụ có đầu ra và phạm vi file rõ ràng. Chỉ chạy song song khi các nhiệm vụ đủ độc lập.

| Vai trò | Ví dụ |
| --- | --- |
| Codex | Xây module A |
| Antigravity | Xây module B không sửa các file của module A |
| Claude Code | Review hoặc xây module C độc lập |

Nếu hai nhiệm vụ cần sửa cùng file, thống nhất thứ tự thực hiện hoặc giao một agent sở hữu file đó. Review có thể diễn ra song song ở chế độ chỉ đọc.

Khi plugin `independent-review` bật, tác giả và reviewer phải là hai phiên/agent khác nhau. Người điều phối giao [yêu cầu review trung tính](reviews/templates/REQUEST.md); reviewer làm lượt độc lập trước khi xem giải thích của tác giả. Xem `reviews/README.md`.

Người điều phối sở hữu `SPEC.md`, `PLAN.md` và `project.plugins.json` trong lúc các nhiệm vụ chạy song song. Agent khác báo thay đổi yêu cầu/tiến độ hoặc đề xuất bật plugin khi bàn giao; người điều phối cập nhật các file này sau khi tích hợp. Nếu `MAP.md` hoặc `contexte/decisions.md` cũng có nhiều người cần sửa, giao quyền sở hữu từng file hoặc gộp các cập nhật khi tích hợp.

Mỗi agent tạo worklog có tên riêng theo `docs/worklog/README.md` trên branch của mình. Khi tích hợp, giữ lại worklog cùng với code; người điều phối có thể dùng các log đó để cập nhật `PLAN.md`.

## Cách ly bằng Git worktree

1. Commit khung dự án và các yêu cầu đã chốt trước khi tách worktree. Thay đổi chưa commit trong checkout hiện tại không tự xuất hiện ở worktree mới.
2. Tạo một branch và thư mục worktree riêng cho mỗi nhiệm vụ. Ví dụ trong PowerShell, chạy tại thư mục repo gốc sau khi đã có commit nền:

```powershell
git worktree add -b codex/module-a ..\setupSourceVibeCode-codex main
git worktree add -b antigravity/module-b ..\setupSourceVibeCode-antigravity main
git worktree add -b claude/module-c ..\setupSourceVibeCode-claude main
```

3. Mở **đúng thư mục worktree** tương ứng trong mỗi công cụ. Không cho ba công cụ cùng sửa checkout gốc.
4. Khi một agent hoàn tất, xem diff, chạy test phù hợp và tạo PR nếu được giao. Nếu plugin `independent-review` bật, reviewer khác làm báo cáo trước. Chỉ chủ repo quyết định merge vào `main` theo `governance/README.md`. Sau mỗi lần merge, cập nhật các branch còn lại và xử lý xung đột nếu có.
5. Chỉ xóa worktree khi thay đổi đã được tích hợp hoặc lưu lại an toàn. Kiểm tra `git status` trước khi dọn.

Ví dụ tên branch và thư mục cần đổi theo nhiệm vụ thực tế. Nếu branch `main` đã đổi tên, dùng branch nền hiện tại thay thế.

## Mẫu giao việc cho mỗi agent

```text
Đọc AGENTS.md, MAP.md, SPEC.md và phần liên quan của PLAN.md.
Nhiệm vụ: <một đầu ra cụ thể>
Branch/worktree: <tên và đường dẫn>
Phạm vi file được sửa: <đường dẫn>
Không sửa: <đường dẫn đang do agent khác phụ trách>
Tiêu chí hoàn thành: <hành vi hoặc kết quả kiểm chứng được>
Kiểm tra cần chạy: <lệnh hoặc cách xác minh>
Bàn giao: tóm tắt thay đổi, file đã sửa, kết quả kiểm tra, đường dẫn worklog, commit/branch, việc còn lại.
```

Agent không tự nhận thêm phạm vi từ nhiệm vụ khác. Nếu gặp phụ thuộc hoặc file dùng chung, báo cho người điều phối trước khi sửa.
