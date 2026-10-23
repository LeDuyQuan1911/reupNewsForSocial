# Review độc lập ảnh bài đăng

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Review độc lập diff 5819b4e074af8ecc7eaf5319c5193adf6fbeb2dd..721cbf38e6f22c20b669fe702f48da9a22fb4ca5 theo yêu cầu `reviews/requests/post-images.md`; chỉ đọc implementation và chạy kiểm tra, không sửa code.

## Thực hiện
Đọc quy tắc, SPEC và diff; xem đường đi lấy ảnh, lưu ảnh, kiểm duyệt và gửi Page. Ghi báo cáo tại `reviews/reports/post-images.md` với hai phát hiện có bằng chứng. Ở vòng đối chiếu, xem bản sửa chưa commit trong checkout chính và cập nhật kết luận cho P1/P2.

## Quyết định
Đánh giá race thay ảnh sau duyệt là P1 vì có thể gửi ảnh chưa được duyệt. Đánh giá rủi ro DNS rebinding là P2 vì đường kiểm tra và kết nối tách rời; chưa thử mạng thật.

## Kiểm chứng
Bản đầu: `python -B -m unittest discover -s tests -v` 15/15 qua; `python -m compileall -q app run.py` qua; tái hiện ảnh duyệt đỏ nhưng ảnh gửi xanh. Sau sửa: test 17/17 qua, `compileall` qua; source dùng cùng byte ảnh cho model và Page, kết nối ảnh ghim IP đã kiểm tra.

## Còn lại
Hai phát hiện đã được xử lý trong bản chưa commit. Chưa thử tích hợp LLM, nguồn báo hoặc Facebook Page thật; chưa thử DNS rebinding trên mạng thật. Cần commit bản sửa trước khi đưa vào quy trình merge.
