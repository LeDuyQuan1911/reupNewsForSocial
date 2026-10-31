# Chẩn đoán ảnh trùng trong bài Facebook

- Ngày: 2026-11-01
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích vì sao hai bài Facebook trong ảnh người dùng gửi có ba ảnh gần như trùng nhau; kiểm tra và sửa bước chọn ảnh nếu source xác nhận nguyên nhân.

## Thực hiện
Đối chiếu hai ảnh chụp Facebook của người dùng với `app/media.py`, `app/database.py`, `app/queue.py` và adapter Meta. Ứng dụng gom tối đa ba ảnh nguồn/AI nhưng chỉ so URL và SHA-256 của JPEG; cùng hình được nén hoặc đổi kích thước có thể vượt qua. Thêm so sánh ảnh thu nhỏ theo hình dạng và màu trong `app/media.py`, áp dụng lúc chọn ảnh nguồn/ảnh bổ sung và lọc lại trước khi gửi Page. Thêm test trong `tests/test_app.py`; cập nhật `SPEC.md`, `README.md`, `PLAN.md`, `contexte/decisions.md`.

## Quyết định
Giữ một ảnh nếu không có hình thứ hai thật sự khác biệt; không tạo ảnh lặp chỉ để đủ ba. Bước lọc khi gửi chỉ chọn ảnh khác biệt, không sửa dữ liệu ảnh của bài đã lên lịch/đã đăng.

## Kiểm chứng
Tái hiện bằng hai JPEG cùng hình nhưng chất lượng nén khác: sau sửa chỉ một bản được thêm; ảnh khác màu/chủ thể vẫn được giữ. Test lọc bài đã lên lịch và ảnh AI bổ sung gần trùng cũng đạt. `python -m unittest discover -s tests -p test_app.py -k image -q` với `REUP_FACEBOOK_AUTH_MODE=page_token`: 27 test đạt. `python -m unittest discover -s tests -p test_automation.py -q`: 27 test đạt. Review độc lập ban đầu phát hiện screenshot cùng bố cục nhưng khác chữ bị lọc nhầm; đã sửa bằng kiểm tra sai khác theo ô và thêm test hồi quy. Vòng đối chiếu xác nhận ảnh khác chữ được giữ, ảnh cùng hình resize/nén lại bị loại; không còn phát hiện đã xác nhận. `git diff --check`: sạch.

## Còn lại
Chưa có dữ liệu ảnh gốc/URL từ hai bài trên server nên không xác nhận cặp URL hoặc file cụ thể nào bị lặp; hai ảnh chụp chỉ cho thấy sự trùng lặp thị giác. Bài Facebook đã đăng không tự thay đổi. Chưa triển khai bản sửa lên server.
