# Làm bài đăng tự nhiên và thu hút hơn

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn các bài AI tạo sau này có icon thay đổi tự nhiên, không áp số lượng cố định, và phần nội dung thu hút người đọc thật sự.

## Thực hiện
Đã đổi prompt để ưu tiên mở bài bằng chi tiết cụ thể, giải thích giá trị cho người đọc và gợi thảo luận có căn cứ. Mỗi lần viết chọn một góc mở bài và dùng nhiệt độ tạo nội dung cao hơn bước kiểm duyệt. Bước dự phòng chọn ngẫu nhiên số lượng, vị trí và loại icon khi model dùng quá ít; không còn bộ bốn icon gắn cố định. Hashtag thiếu được bổ sung với số lượng tối thiểu, nguồn luôn ở cuối. Đã cập nhật SPEC.md, PLAN.md và test.

## Quyết định
Giữ tính chính xác theo nguồn; không dùng câu giật gân thiếu căn cứ hoặc bịa dữ kiện. Để model chọn icon tự nhiên trước, chỉ dùng ngẫu nhiên ở bước dự phòng. Bài đã đăng và các bản nháp cũ giữ nguyên.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 45 test đạt, gồm test số lượng/icon dự phòng thay đổi qua nhiều lần. Tạo hai bản nháp thử qua 9Router từ cùng nguồn công khai: mở bài khác nhau, bộ icon lần lượt 4 và 3, mỗi bài có 4 hashtag, nguồn ở cuối; không lưu hoặc đăng. Dashboard và 9Router đã khởi động, cổng localhost 5000/20128 lắng nghe và `/posts` trả HTTP 200. Không có bài đăng thật nào đến hạn khi khởi động lại.

## Còn lại
Chất lượng thu hút người đọc chưa thể bảo đảm chỉ bằng prompt; bước viết hiện vẫn dựa trên tiêu đề/tóm tắt nguồn. Cần đánh giá kết quả thực tế của các bài mới và cải thiện khi có mẫu giọng văn cụ thể hơn.
