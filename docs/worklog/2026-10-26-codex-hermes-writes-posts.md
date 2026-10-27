# Hermes viết bản nháp trong dashboard

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Nối thao tác viết lại và luồng tự tạo bài với Hermes, để Hermes trực tiếp soạn bài theo ngữ cảnh biên tập của repo; giữ việc duyệt và đăng riêng.

## Thực hiện
Phát hiện `app/llm.py` từng gọi endpoint chat 9Router trực tiếp, còn Hermes chỉ chạy ở terminal riêng. Thêm `app/hermes_writer.py` gọi Hermes CLI chế độ một lượt, nạp `docs/editorial-brief.md` cùng trích đoạn bài gốc/README và metadata qua stdin. Cả nút viết lại và bước chuẩn bị tự động đều đi qua hàm này. Đổi nhãn giao diện, cập nhật README/MAP/SPEC/PLAN/AGENTS và quyết định dự án. Dùng Hermes thật tạo và lưu bản nháp mới cho bài #25; không gọi chức năng đăng Facebook.

## Quyết định
Hermes viết toàn bộ nội dung, dashboard chỉ kiểm tra icon, bổ sung hashtag dự phòng và chuẩn hóa liên kết nguồn. Dùng toolset trống và không nạp rules coding trong lời gọi viết bài để dữ liệu nguồn không thể khiến Hermes dùng công cụ; brief biên tập vẫn được truyền rõ trong mỗi lượt. Hermes lỗi thì giữ bản nháp cũ, không fallback sang lời gọi model trực tiếp. Các bước chọn tin, tạo/duyệt ảnh và kiểm duyệt giữ đường 9Router hiện có.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 63 bài kiểm tra đạt. Gọi Hermes thật qua 9Router với bài #25: trả nội dung có emoji, hashtag và URL nguồn; bài vẫn là bản nháp. Kiểm tra một lượt Hermes khác với toolset trống: trả bài hợp lệ có emoji. Khởi động lại dashboard; GET `/posts/25` trả HTTP 200 và hiển thị nút Hermes cùng icon trong bản nháp. `git diff --check` đạt.

## Còn lại
Hermes khởi tạo tiến trình mới mỗi bài nên chậm hơn lời gọi API trực tiếp. Trích đoạn nguồn có thể không đọc được khi trang chặn tự động; bài đó chỉ dựa trên metadata. Chưa đăng Facebook từ thay đổi này. Không commit/push/merge vì yêu cầu này chưa đề nghị.
