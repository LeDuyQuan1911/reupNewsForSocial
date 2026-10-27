# Icon theo mục đích từng dòng bài đăng

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn nhiều icon, đặt ở đầu từng dòng ý chính để biểu đạt nội dung dòng đó; số icon thay đổi theo số ý của bài.

## Thực hiện
Đã sửa prompt để viết mỗi ý chính thành một dòng có icon ở đầu, chọn theo vai trò dòng (tin mới, số liệu, chi tiết kỹ thuật, lợi ích, thao tác, câu hỏi). Bước dự phòng duyệt từng dòng nội dung, giữ icon model đã chọn và bổ sung icon đúng vai trò khi thiếu; số icon theo số dòng. Cập nhật test, SPEC.md và PLAN.md. Siết prompt để tránh khẳng định lợi ích chưa có căn cứ.

## Quyết định
Để model chọn icon theo nghĩa của từng dòng trước; khi thiếu, bổ sung icon theo vai trò của dòng với lựa chọn ngẫu nhiên trong nhóm biểu tượng phù hợp. Không sửa bài đã đăng hoặc bản nháp cũ.

## Kiểm chứng
`python -m unittest discover -s tests -v`: 47 test đạt, gồm kiểm tra icon đầu từng dòng, vai trò icon cho số liệu/câu hỏi và số icon theo số dòng. Một bản nháp thử qua 9Router từ nguồn công khai có icon ở đầu bảy dòng nội dung, hashtag và nguồn ở cuối; không lưu hoặc đăng. Dashboard và 9Router đã khởi động, cổng localhost 5000/20128 lắng nghe, `/posts` trả HTTP 200. Không có bài đăng thật nào đến hạn khi khởi động lại.

## Còn lại
Việc chọn vai trò icon theo từ khóa chỉ là dự phòng nên có thể chưa đúng mọi ngữ cảnh; model được ưu tiên chọn icon trước. Bước viết hiện dựa trên tiêu đề/tóm tắt nguồn, chưa kiểm chứng toàn văn.
