# Plugin: Codebase graph

Source Understand Anything đã nằm trong `vendor/understand-anything/understand-anything-plugin/`; mọi agent dùng cùng bản được commit trong repo. Xem [hướng dẫn](../../docs/understand-anything.md).

- Khi cần graph để đọc kiến trúc hoặc tác động của diff, chạy `node scripts/graph-status.mjs` trước. Nếu `MISSING` hoặc `STALE`, đọc skill vendored `vendor/understand-anything/understand-anything-plugin/skills/understand/SKILL.md` và tạo/cập nhật graph với `--language vi`. Chỉ dùng graph sau khi trạng thái `CURRENT` hoặc ghi rõ giới hạn nếu cập nhật thất bại.
- `MAP.md` là bản đồ thủ công của repo, vẫn đọc bình thường khi bắt đầu nhiệm vụ. Không tự chạy LLM chỉ vì đọc file này.
- Trong worktree đặt `UNDERSTAND_NO_WORKTREE_REDIRECT=1` trước khi chạy skill để graph không bị ghi vào checkout chính.
- Hook `post-commit` chỉ đánh dấu graph cũ. Nó không gọi LLM; lần dùng graph tiếp theo mới làm mới theo yêu cầu người dùng.
- Không coi graph là bằng chứng đủ cho review. Kiểm tra lại diff, source và test; giữ review độc lập nếu plugin `independent-review` bật.
- Graph nằm trong `.ua/` cục bộ, hoặc `.understand-anything/` nếu thư mục dữ liệu cũ đã tồn tại; không được commit hoặc chia sẻ trước khi rà soát dữ liệu nhạy cảm.

Nếu phụ thuộc của runtime vendored chưa được build, làm theo hướng dẫn để cài từ lockfile. Nếu skill không chạy được, đọc source trực tiếp và ghi giới hạn trong worklog.
