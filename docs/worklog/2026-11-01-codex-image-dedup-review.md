# Review độc lập chống ảnh gần trùng

- Ngày: 2026-11-01
- Agent: Codex reviewer độc lập
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Review chỉ đọc diff chưa commit từ `f01b0c7b` trong `app/media.py`, `tests/test_app.py` và tài liệu liên quan. Đánh giá loại ảnh gần trùng dù khác kích thước/chất lượng JPEG khi chuẩn bị và trước khi gửi Facebook, giữ ít nhất một ảnh hợp lệ. Không đọc worklog tác giả trước báo cáo đầu tiên; không sửa implementation.

## Thực hiện
Đã đối chiếu diff, đường chuẩn bị ảnh và đường gửi Page. Lưu báo cáo độc lập rồi cập nhật vòng đối chiếu tại `reviews/reports/image-dedup-independent.md`. Tác giả sửa phát hiện P2; reviewer không sửa implementation và không đọc worklog tác giả trước báo cáo đầu tiên.

## Quyết định
Phát hiện P2 vòng đầu: screenshot khác chữ nhưng cùng bố cục/nền bị coi là trùng. Bản sửa dùng sai khác theo ô 16×16 trên ảnh 128×128; mẫu độc lập và test hồi quy nay phân biệt được ảnh khác chữ. Rút P2 khỏi lỗi còn mở; chưa kết luận về tần suất trên ảnh thật.

## Kiểm chứng
Bốn test liên quan đạt; `git diff --check` không có lỗi whitespace. Thử độc lập ảnh khác chữ nay trả `False`; ảnh cùng hình resize/nén khác nhau trả `True`; screenshot nhiều chữ resize/nén trả `True`; bảng màu khác nhau trả `False`. Chưa đăng Facebook thật.

## Còn lại
Không còn phát hiện đã xác nhận. Chưa đo trên tập ảnh nguồn thực tế hoặc đăng Facebook thật.
