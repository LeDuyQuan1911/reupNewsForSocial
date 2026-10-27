# Kiểm tra điều kiện để thử đăng nhóm local

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng hỏi bước cần làm ngay để thử agent local đăng vào nhóm. Kiểm tra dịch vụ/model và trình duyệt hiện có; không truy cập tài khoản Facebook hoặc đăng bài.

## Thực hiện
Đã kiểm tra cấu hình plugin, biến môi trường ở dạng có/không, Playwright và Chrome. Khởi động lại 9Router và dashboard bằng script repo; cả cổng 20128 và 5000 lắng nghe trên localhost. Không mở Facebook hoặc đọc thông tin phiên đăng nhập.

## Quyết định
Chuẩn bị môi trường hiện có trước. Chưa xây phần đăng nhóm khi chưa biết nhóm đích và danh tính đăng; các thông tin này quyết định phiên Facebook và cách xác nhận quyền đăng. Không giả định 9Router đang chạy đồng nghĩa model Hermes đã được host local.

## Kiểm chứng
`node scripts/plugins.mjs check`: hợp lệ. Chrome và Playwright có sẵn; ba biến Facebook Page chưa đặt. Script khởi động trả `port_5000=True`, `port_20128=True`. Chạy `node scripts/check-worklog.mjs` trước bàn giao.

## Còn lại
Cần URL một nhóm, danh tính đăng (tài khoản cá nhân/Page), phiên Facebook đăng nhập thủ công và xác nhận endpoint/model Hermes local nếu muốn thay model hiện tại. Chưa có adapter đăng nhóm và chưa đăng bài.
