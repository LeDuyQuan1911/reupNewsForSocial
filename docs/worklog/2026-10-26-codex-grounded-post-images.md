# Chọn ảnh bám sát bài gốc và repo

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Ưu tiên ảnh thật từ bài báo hoặc repo và ảnh chụp phần liên quan trên trang nguồn; ảnh tạo mới phải thể hiện đúng nội dung hoặc luồng xử lý của bài.

## Thực hiện
`app/media.py` thử nhiều ảnh từ bài báo, bỏ qua ảnh không dùng được, ưu tiên ảnh đủ lớn trong README repo và sau đó mới chụp repo. `app/database.py` và `app/templates/post.html` lưu/hiển thị nguồn ảnh README. `app/llm.py` yêu cầu model nhìn ảnh kiểm tra mức độ liên quan trước khi đăng. Thay ảnh minh họa chung của bản nháp #1 bằng ảnh AI thể hiện luồng đánh giá hệ thống AI, nhận diện lỗ hổng và tăng cường biện pháp bảo vệ được bài gốc nêu. Bản nháp #20 giữ ảnh Microduck thật từ bài NVIDIA. Cập nhật README, SPEC, PLAN, quyết định kỹ thuật và test.

## Quyết định
Ảnh thẻ chỉ dùng xem trước khi không lấy được tư liệu thật; bài chỉ có ảnh này không được đăng thật theo quy tắc đã triển khai. Ảnh AI phải mô tả chủ đề/quy trình có căn cứ từ nguồn, không trình bày như ảnh sự kiện thật.

## Kiểm chứng
`python -m unittest discover -s tests -p 'test_*.py'`: 50 test đạt. Flask test client: trang và ảnh của bản nháp #1, #20 đều HTTP 200; kiểm tra hai ảnh trực quan. Máy hiện không truy cập được DNS công khai từ tiến trình shell, nên kiểm thử tải ảnh nguồn trực tiếp dùng mock.

## Còn lại
Ứng dụng chưa có bước chụp màn hình bài báo tùy ý; khi bài báo không có ảnh dùng được, cần thêm ảnh thủ công hoặc ảnh AI đúng nội dung. Chưa thử phản hồi thật của model vision 9Router về độ liên quan ảnh. Server localhost hiện không chạy.
