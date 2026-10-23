# Cài và kết nối 9Router cục bộ

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn chạy 9Router tại localhost và dùng được với ứng dụng hiện tại.

## Thực hiện
Đã xác nhận ứng dụng mặc định gọi `http://127.0.0.1:20128/v1`. Cài gói npm chính thức `9router@0.5.109` toàn cục và khởi chạy CLI với `--host 127.0.0.1 --port 20128 --no-browser --skip-update`. Không sửa code ứng dụng vì endpoint mặc định đã đúng.

## Quyết định
Chọn npm vì Node/npm có sẵn còn Docker daemon không chạy. Buộc dịch vụ chỉ lắng nghe localhost vì CLI mặc định là `0.0.0.0`. Không ghi token hoặc giá trị bí mật vào repo/worklog.

## Kiểm chứng
`npm view 9router` xác nhận phiên bản 0.5.109; `npm install -g 9router@0.5.109` thành công; `9router --help` xác nhận tùy chọn host/port. `Get-NetTCPConnection` cho thấy listener `127.0.0.1:20128`; `GET /dashboard` chuyển đến `/login`; `GET /v1/models` trả HTTP 200. Chưa gửi chat completion vì chưa chọn và cấu hình provider/model.

## Còn lại
Người dùng cần đăng nhập dashboard 9Router, thêm provider hoặc tài khoản và chọn model có khả năng xem ảnh. Sau đó đặt `REUP_LLM_MODEL` và `REUP_LLM_VISION_MODEL` trong môi trường chạy ứng dụng, khởi động lại ứng dụng để nạp biến. Danh mục `/v1/models` là danh mục model, chưa chứng minh provider nào đã được cấp quyền. Tiến trình 9Router hiện chỉ chạy trong phiên máy này, chưa thiết lập tự khởi động cùng Windows.
