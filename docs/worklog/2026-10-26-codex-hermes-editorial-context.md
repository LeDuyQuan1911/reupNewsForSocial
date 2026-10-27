# Cấu hình LLM và context biên tập Hermes

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Xác định vì sao bài viết lại bằng LLM không có icon; chỉnh luồng viết để icon có ý nghĩa mà số lượng/vị trí do model quyết định. Kiểm tra kết nối LLM và đưa yêu cầu biên tập đã chốt vào context Hermes, không đưa secret vào repo.

## Thực hiện
Kiểm tra bài #25 thấy không có emoji vì `app/llm.py` chỉ cho phép dùng tùy ý. Chỉnh prompt yêu cầu ít nhất một emoji có ý nghĩa, để LLM tự chọn số lượng/vị trí; nếu thiếu thì viết lại một lần, vẫn thiếu thì giữ bản nháp cũ. Loại dòng URL nguồn trùng. Bổ sung yêu cầu biên tập vào `AGENTS.md`, thêm `scripts/start-hermes.ps1` để Hermes nạp context tại repo, cập nhật tài liệu và test. Cấu hình lại Hermes dùng model văn bản hiện có qua 9Router; kiểm tra kết nối. Viết lại và lưu bài #25 ở trạng thái bản nháp, có icon và một link nguồn. Khởi động lại dashboard.

## Quyết định
Context Hermes gắn với workspace qua `AGENTS.md`, không ghi vào persona toàn cục hoặc file secret. Dashboard gọi 9Router trực tiếp, nên sửa prompt dashboard riêng; Hermes không thay thế tác vụ tự động của dashboard. Không đăng bài #25.

## Kiểm chứng
`scripts/setup-hermes.ps1 -TestConnection` trả `OK`. `scripts/start-hermes.ps1 -Prompt ...` trả đúng quy tắc icon từ context repo. Gọi `llm.write_draft` thật qua 9Router trên bài #25 tạo icon ở đoạn phù hợp; đã xem bản nháp trước khi lưu. `python -m unittest discover -s tests -q`: 61 test đạt. Dashboard sau khi khởi động lại trả HTTP 200 tại `/posts/25`, trang có icon. `git diff --check`: đạt.

## Còn lại
Model yếu có thể chọn icon hoặc cách diễn đạt chưa thật hay; cần người dùng xem các bản nháp trước khi xuất bản. Bài đã lên lịch/đã đăng không tự đổi. Các thay đổi code chưa commit và cần review độc lập trước khi merge `main`.
