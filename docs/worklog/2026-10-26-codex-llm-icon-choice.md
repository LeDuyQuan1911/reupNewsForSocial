# Để LLM tự chọn cách dùng icon

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Không ép mỗi dòng bài viết có icon. LLM quyết định vị trí và số icon theo nội dung từng bài; điều chỉnh luồng tạo bản nháp và tài liệu liên quan.

## Thực hiện
Sửa `app/llm.py`: bỏ bộ quy tắc chọn icon theo vai trò và vòng lặp tự chèn icon đầu mỗi dòng. Prompt yêu cầu LLM tự chọn số lượng, vị trí và loại emoji theo nội dung bài. Cập nhật `tests/test_llm_style.py`, `SPEC.md` và `PLAN.md`.

## Quyết định
Giữ phần đảm bảo liên kết nguồn và hashtag; không xử lý lại emoji sau khi LLM trả lời. Bản nháp cũ không tự thay đổi.

## Kiểm chứng
`python -m unittest discover -s tests -p 'test_*.py'`: 47 test đạt. `git diff --check` cho các file sửa: đạt.

## Còn lại
Chưa thử đầu ra với model 9Router thực tế. Cần tạo bản nháp mới hoặc bấm viết lại trên bài muốn áp dụng; thao tác viết lại sẽ thay nội dung bản nháp hiện có.
