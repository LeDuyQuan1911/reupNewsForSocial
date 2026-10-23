# Hiển thị luồng từ nguồn tin đến thời điểm đăng

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thêm một workflow trong dashboard thể hiện nguồn → bài báo → đăng lên đâu → lúc mấy giờ, dựa trên dữ liệu thực tế của ứng dụng.

## Thực hiện
Thêm truy vấn ghép `sources`, `articles`, `posts` trong `app/database.py`, route `/workflow` trong `app/web.py` và template `app/templates/workflow.html`. Mỗi dòng cho thấy bốn bước có liên kết tới trang nguồn, chi tiết bài báo và bài đăng. Mặc định hiển thị bài có bản nháp; có chế độ xem mọi bài báo. Thêm điều hướng và liên kết từ Tổng quan, CSS responsive, test, README, SPEC, MAP và PLAN.

## Quyết định
Hiển thị Facebook Page là kênh hiện được hỗ trợ khi bài đã có bản nháp; bài chưa có bản nháp để trạng thái chưa chọn đích/giờ. Phân biệt giờ dự kiến với giờ đăng thực tế. Chỉ có 7 bản nháp trong 85 bài báo cục bộ, nên mặc định hiện nhóm đã chọn đăng và cho chuyển sang toàn bộ bài báo.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 20/20 test đạt. `python -m compileall -q app run.py`: đạt. `git diff --check`: đạt. `node scripts/plugins.mjs check`: hợp lệ. Khởi động lại Flask, HTTP `/workflow` trả 200; xem trang trực quan trong trình duyệt Codex ở màn hình hẹp. Đã thử mở phần “Cách đọc luồng” và chuyển qua lại hai chế độ xem.

## Còn lại
Chỉ hỗ trợ Facebook Page; chưa có đích đăng riêng theo từng bài hoặc tích hợp trang cá nhân/nhóm/LinkedIn. Dữ liệu hiện tại chưa có bài đã lên lịch hoặc đã đăng để quan sát trực tiếp; các trạng thái này được kiểm tra bằng test. Chưa review độc lập hoặc tạo PR; cần review trước khi merge vào `main`.
