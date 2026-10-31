# Báo cáo review: image-dedup

- Reviewer: Codex reviewer độc lập
- Ngày: 2026-11-01
- Base / head: `f01b0c7be70767546d6b869f430e3d9ed17e67b8` / cùng HEAD, diff chưa commit
- Vòng: đối chiếu (sau báo cáo độc lập)
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff `app/media.py`, `tests/test_app.py`, `README.md`, `SPEC.md`, `PLAN.md`, `contexte/decisions.md`; đối chiếu đường gửi trong `app/queue.py` và `app/facebook.py`. Không đọc worklog tác giả trước báo cáo này.
- Lệnh đã chạy và kết quả: bốn test `similar_layout`, `same_picture`, `publish_filters_visual_duplicates`, `generated_companion_matching` đều đạt sau bản sửa; `git diff --check` không báo lỗi whitespace. Mẫu độc lập ảnh “FIRST PRODUCT” so với “RELEASE NOTES” và “HELLO WORLD” nay trả `False`; các biến thể cùng hình resize xuống 900×506, 600×337, 320×180 và 160×90 vẫn trả `True`. Mẫu screenshot nhiều dòng chữ resize/nén cũng trả `True`; các bảng màu nội dung khác nhau trả `False`.
- Phần chưa kiểm chứng: chưa đăng Facebook thật; chưa đo false positive/false negative trên tập ảnh thực tế từ các nguồn của dự án.

## Phát hiện

### P2 — Ảnh screenshot khác nội dung chữ bị bỏ như ảnh trùng

- Vị trí: `app/media.py:57-60`
- Điều kiện kích hoạt / cách tái hiện: hai JPEG có cùng kích thước, nền tối và khung giống nhau, nhưng dòng chữ lớn ở giữa khác hẳn. Trong thử độc lập, ảnh đầu ghi “FIRST PRODUCT”; ảnh thứ hai lần lượt ghi “RELEASE NOTES” hoặc “HELLO WORLD”.
- Kết quả thực tế: `visually_duplicate(second, [first])` trả `True`. `prepare_post_image()` bỏ ảnh thứ hai ở dòng 397; với bài đã lên lịch, `publishable_post_image_paths()` bỏ ảnh đó ở dòng 295. Bài vẫn có ảnh đầu nhưng mất screenshot chứa nội dung khác.
- Kết quả mong đợi: chỉ bỏ ảnh cùng hình dù resize hoặc nén lại; giữ ảnh có nội dung chủ thể/chữ khác nhau để người đọc thấy đúng các tư liệu bổ sung.
- Bằng chứng: hàm chấp nhận khoảng cách dHash tối đa 8 và sai khác trung bình màu tối đa 22 trên ảnh thu nhỏ 32×32. Bố cục/nền giống nhau làm hai điều kiện này đạt dù chữ khác; ba test mới chỉ dùng cùng một hình nén lại, chưa kiểm tra screenshot khác chữ.
- Độ chắc chắn: cao với mẫu tái hiện; mức phổ biến trên ảnh nguồn thật chưa đo.
- Hướng sửa gợi ý: thêm test hai screenshot cùng bố cục nhưng thông tin khác; dùng kiểm tra giữ chi tiết chữ/chủ thể hoặc ngưỡng chặt hơn sau bước nhận diện resize/nén.

## Đối chiếu sau phản hồi tác giả

Phát hiện P2 được xác nhận ở bản đầu rồi đã sửa. Bản mới so ảnh ở 128×128 và yêu cầu sai khác trên từng ô 16×16 không vượt ngưỡng (`app/media.py:58-63`); test hồi quy `tests/test_app.py:896-906` kiểm tra hai screenshot khác chữ. Mẫu tái hiện độc lập “FIRST PRODUCT”/“RELEASE NOTES” nay được giữ, còn ảnh cùng hình khi resize hoặc nén lại vẫn được loại. Rút phát hiện P2 khỏi danh sách lỗi còn mở.

## Kết luận cho chủ repo

Phát hiện P2 của vòng độc lập đã được xử lý và kiểm chứng bằng mẫu độc lập cùng test hồi quy. Không còn phát hiện đã xác nhận trong phạm vi review này. Chưa đo bộ lọc trên tập ảnh nguồn thực tế hoặc đăng Facebook thật; reviewer không quyết định merge.
