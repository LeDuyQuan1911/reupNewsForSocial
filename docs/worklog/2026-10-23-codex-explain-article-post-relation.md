# Giải thích quan hệ bài báo và bài đăng

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích quan hệ giữa “Bài báo” và “Bài đăng” theo source hiện tại, không sửa ứng dụng.

## Thực hiện
Đọc schema `articles`/`posts` trong `app/database.py`, hàm `make_draft`, các route trong `app/web.py` và trang chi tiết bài báo. Xác nhận mỗi bài đăng tham chiếu đúng một bài báo; một bài báo có tối đa một bài đăng.

## Quyết định
Giải thích theo dữ liệu và luồng đang chạy, không suy rộng thành khả năng đăng nhiều kênh chưa được xây.

## Kiểm chứng
Đối chiếu `posts.article_id INTEGER NOT NULL UNIQUE REFERENCES articles(id)`, `INSERT OR IGNORE` trong `make_draft`, route tạo nháp và route biên tập/đăng. Không chạy test vì chỉ khảo sát, không sửa code.

## Còn lại
Không có.
