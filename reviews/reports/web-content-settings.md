# Báo cáo review: web-content-settings

- Reviewer: Codex (agent độc lập)
- Ngày: 2026-11-01
- Base / head: `f01b0c7be70767546d6b869f430e3d9ed17e67b8` / `829a90af`
- Vòng: đối chiếu (lượt độc lập đã lưu tại head `47b93e1b`)
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff code và test thuộc yêu cầu, schema/migration SQLite, form Hermes và CSRF, Hermes web discovery, ranking RSS/GitHub, viết bài/bình luận thủ công và tự động, giới hạn claim mỗi ngày, brief biên tập.
- Lệnh đã chạy và kết quả: Lượt độc lập tại `47b93e1b`: 132 test, 1 fail; Hermes writer 5 pass, Hermes research 9 pass. Lượt đối chiếu tại `829a90af` với `REUP_FACEBOOK_AUTH_MODE=page_token`, `REUP_HERMES_DISCOVERY_ENABLED=0`: `test_llm_style.py` 4 pass, `test_automation.py` 29 pass, toàn bộ suite 133 pass.
- Phần chưa kiểm chứng: Không gọi Hermes/model/Meta thật, không kiểm tra giao diện bằng trình duyệt. Chưa thử migration trên bản sao dữ liệu sản xuất.

## Phát hiện

### P2 — Chỉnh brief làm hỏng test hiện có

- Vị trí: `docs/editorial-brief.md:7`
- Điều kiện kích hoạt / cách tái hiện: Chạy `python -m unittest discover -s tests -p 'test_llm_style.py' -q`.
- Kết quả thực tế: `test_prompt_leaves_icon_choice_to_model` thất bại vì test tìm `Không áp công thức một icon đầu mỗi dòng`, còn brief mới dùng `không áp...` sau dấu chấm phẩy.
- Kết quả mong đợi: Bộ test hiện có đạt, đồng thời brief tiếp tục trao quyền chọn vị trí icon cho model.
- Bằng chứng: `tests/test_llm_style.py:42`; suite đầy đủ chạy 132 test và fail đúng assertion này.
- Độ chắc chắn: cao
- Hướng sửa gợi ý (nếu có): Giữ câu brief theo cách khớp điều kiện test hoặc cập nhật test nếu cách diễn đạt mới là chủ ý.

### P2 — Ưu tiên tìm tin không tác động tới ranking RSS/GitHub khi tìm web tắt

- Vị trí: `app/hermes_research.py:190`
- Điều kiện kích hoạt / cách tái hiện: Lưu `research_focus` khác mặc định trên trang Hermes, giữ `REUP_HERMES_DISCOVERY_ENABLED=0`, rồi chạy chu kỳ automation với tin RSS/GitHub mới.
- Kết quả thực tế: `hermes_research.find_articles` thoát sớm khi tắt, còn `research.review_candidates` vẫn dùng prompt cố định và không đọc `content_settings`. Tin nguồn RSS/GitHub được chọn theo ưu tiên cũ, bất kể giá trị đã lưu.
- Kết quả mong đợi: Ưu tiên tìm tin đã lưu ảnh hưởng đến lượt chọn tin tự động tiếp theo, hoặc giao diện/phạm vi yêu cầu nói rõ ưu tiên này chỉ dành cho Hermes tìm web.
- Bằng chứng: `app/hermes_research.py:180-190`; `app/automation.py:220-225`; `app/research.py:47-70`; `SPEC.md:39` yêu cầu lượt tìm tiếp theo đọc cấu hình mới ở cả web và automation.
- Độ chắc chắn: vừa
- Hướng sửa gợi ý (nếu có): Truyền ưu tiên đã lưu vào prompt ranking metadata, giữ nguyên giới hạn xác minh và phân bố nguồn.

## Đối chiếu sau phản hồi tác giả

Đã xem diff `47b93e1b...829a90af` và chạy lại kiểm tra trong worktree review. Phát hiện về test brief được **giải quyết**: `docs/editorial-brief.md:7` khôi phục đúng chuỗi mà test yêu cầu; `test_llm_style.py` chạy 4/4 pass. Phát hiện về ưu tiên RSS/GitHub được **giải quyết**: `app/research.py:68,77` đọc `research_focus` từ SQLite và đưa vào prompt xếp hạng; test mới `tests/test_automation.py:572` xác nhận giá trị đã lưu tới lời gọi ranking khi Hermes tìm web tắt. Không có phát hiện mới trong phần diff sửa lỗi.

## Kết luận cho chủ repo

Hai phát hiện ở lượt độc lập đã được giải quyết tại `829a90af`; toàn bộ 133 test đạt. Giới hạn kiểm chứng thực tế nêu trên vẫn còn. Reviewer không quyết định merge.
