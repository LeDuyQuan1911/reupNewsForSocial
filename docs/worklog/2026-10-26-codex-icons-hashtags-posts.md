# Bổ sung icon và hashtag cho bài đăng

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn các bài đăng tạo sau này có nhiều icon và hashtag. Bài đã đăng giữ nguyên.

## Thực hiện
Đã đổi prompt viết bài AI để yêu cầu 4–6 icon và 3–5 hashtag liên quan; thêm bước dự phòng khi model bỏ sót và giữ liên kết nguồn ở cuối. Thêm kiểm tra cho bản nháp thiếu hoặc đã có sẵn icon/hashtag. Cập nhật yêu cầu và kế hoạch.

## Quyết định
Giữ icon và hashtag liên quan nội dung, tránh tạo dữ kiện mới hoặc spam thẻ. Dùng hashtag công nghệ chung khi model không tạo đủ. Không sửa các bài đã đăng và không ghi token vào repo.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 44 test đạt. `git diff --check` không có lỗi khoảng trắng. 9Router và dashboard lắng nghe trên localhost; `/posts` trả HTTP 200. Thử gọi model đã cấu hình bằng dữ liệu công khai, đầu ra có 4 icon, 4 hashtag và nguồn ở cuối; không lưu hoặc đăng bài thử. Không đưa token vào file theo dõi bởi Git.

## Còn lại
Áp dụng cho lần gọi viết bản nháp mới bằng AI; các bản nháp đã có và bài đã đăng giữ nguyên. Chưa kiểm tra một chu kỳ quét và đăng tự động trọn vẹn sau thay đổi.
