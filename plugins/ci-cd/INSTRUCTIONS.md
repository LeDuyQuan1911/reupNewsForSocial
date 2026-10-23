# Plugin: CI/CD

Khi plugin này bật, CI/CD là một hạng mục phải được lên kế hoạch. Trước khi tạo workflow, xác định stack, lệnh build/test, nền tảng lưu Git, môi trường triển khai, điều kiện phát hành và nơi giữ secrets. Nếu thiếu đích triển khai, hỏi người dùng rồi ghi CD là việc đang chờ; không tuyên bố đã có CD.

1. CI: chạy các kiểm tra có thật trong repo trên thay đổi được đề xuất; tránh job giả chỉ để hiện màu xanh.
2. CD: chỉ triển khai tới môi trường được chỉ định, với cơ chế kích hoạt và quyền truy cập tối thiểu. Không ghi secrets vào workflow hoặc repo.
3. Ghi cách kiểm tra pipeline, cách xem lỗi và cách rollback phù hợp với đích triển khai.
4. Xác minh workflow bằng cách phù hợp với nền tảng; lần chạy production cần được người dùng cho phép trong nhiệm vụ liên quan.

Không tự tạo workflow cho một nhà cung cấp chỉ vì repo có remote Git.
