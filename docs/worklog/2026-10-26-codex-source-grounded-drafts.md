# Bản nháp và ảnh bám sát nguồn

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Áp dụng cách làm từ mẫu đã phân tích: dùng nguồn hiện có (báo chính thức và GitHub), viết lại bài tiếng Việt hấp dẫn và chọn ảnh thật dễ nhận biết từ nguồn/repo/demo. Chưa bổ sung Reddit hoặc Threads làm nguồn quét.

## Thực hiện
Thêm `app/source_content.py` để đọc trích đoạn bài gốc hoặc README GitHub qua bộ tải URL công khai có sẵn. Nối bước này vào viết bản nháp thủ công và tự động trong `app/llm.py`, `app/web.py`, `app/automation.py`; sửa prompt để ưu tiên chi tiết cụ thể, không suy diễn và tự chọn cách dùng emoji. Sắp ảnh demo/screenshot trong README trước ảnh trang trí tại `app/media.py`. Bổ sung test và cập nhật `README.md`, `MAP.md`, `SPEC.md`, `PLAN.md`, `contexte/decisions.md`.

## Quyết định
Giữ nguồn quét RSS/Atom, sitemap chính thức và GitHub ở bước này; Reddit/Threads để adapter tương lai. Nếu trang nguồn không cho đọc, bản nháp chỉ dùng metadata hiện có. Không thay đổi bài đã lưu hoặc gửi Facebook trong nhiệm vụ này.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 60 test đạt. Thử đọc README `google/artemis`: lấy được 6000 ký tự và 9 ảnh ứng viên; thử bài NVIDIA và Anthropic: lấy được trích đoạn, trong khi OpenAI trả HTTP 403 và sẽ dùng metadata. Đã khởi động lại dashboard và kiểm tra localhost:5000 trả HTTP 200. `git diff --check`: đạt. Rà soát diff không thấy secret mới.

## Còn lại
Chưa thử LLM 9Router thật với prompt mới, chưa đối chiếu ảnh bằng người biên tập hoặc xác nhận quyền sử dụng ảnh nguồn. Một số trang chặn tải sẽ chỉ có metadata. Reddit/Threads chưa được quét. Cần review độc lập trước khi dự kiến merge vào `main`.
