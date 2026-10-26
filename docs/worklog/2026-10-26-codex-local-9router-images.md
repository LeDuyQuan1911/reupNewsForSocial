# Xử lý ảnh qua 9Router cục bộ

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Đưa các bước AI tạo, chọn và kiểm tra ảnh của ứng dụng qua endpoint 9Router chạy trên máy người dùng; không dùng dịch vụ tạo ảnh riêng của phiên chat cho luồng ứng dụng.

## Thực hiện
Đã kiểm tra API model của 9Router trên máy: model văn bản/vision hiện tại và model ảnh `ag/gemini-3.1-flash-image` là hai model riêng. Cấu hình `REUP_LLM_IMAGE_MODEL` ở biến môi trường người dùng, không ghi khóa truy cập vào repo.

Ứng dụng lập dàn ý ảnh từ tiêu đề/tóm tắt bằng model văn bản 9Router rồi tạo ảnh qua `/v1/images/generations`. Khi không tìm được ảnh thật từ bài báo, README hoặc ảnh chụp repo, luồng chuẩn bị ảnh thử model ảnh; ảnh vẫn đi qua kiểm tra vision trước khi đăng tự động. Giao diện tài khoản hiển thị tình trạng model ảnh và trang bài đăng phân biệt ảnh do 9Router tạo. Cập nhật `.env.example`, `app/llm.py`, `app/media.py`, `app/database.py`, `app/web.py`, các template, kiểm thử và tài liệu liên quan.

Đã tạo ảnh minh họa có tên chủ thể và sơ đồ nội dung chính qua 9Router, gắn vào bản nháp #1 với loại `router_generated`. Bản nháp vẫn chưa đăng.

## Quyết định
Giữ model văn bản/vision hiện tại cho lập dàn ý và đánh giá; dùng model ảnh riêng của cùng 9Router để sinh ảnh. Chỉ cho phép endpoint tạo ảnh qua địa chỉ loopback. Việc tải/chụp/định dạng ảnh nguồn vẫn là thao tác mã thông thường; các bước AI đi qua 9Router.

## Kiểm chứng
`python -m py_compile app/llm.py app/media.py app/database.py app/web.py`: đạt. `python -m unittest discover -s tests -p 'test_*.py'`: 53 kiểm thử đạt. Đã gọi API ảnh 9Router thật để tạo ảnh cho bản nháp #1 và xem ảnh trực quan. Sau lần sửa cuối, kiểm thử mô phỏng xác nhận đường gọi text planning và image generation.

## Còn lại
9Router chạy trên localhost nhưng nhà cung cấp model có thể xử lý suy luận từ xa; đây không phải LLM chạy offline. Chất lượng hình sinh cần được kiểm tra bằng vision và có thể cần người xem lại trước khi đăng. Chưa gọi lại luồng tích hợp cuối với API thật sau khi bổ sung bước lập dàn ý; từng endpoint đã được gọi thành công riêng.
