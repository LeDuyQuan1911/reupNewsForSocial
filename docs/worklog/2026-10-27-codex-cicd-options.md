# Khảo sát phương án CI/CD cho máy chạy riêng

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Đề xuất các phương án kiểm thử, phát hành và cập nhật repo từ máy phát triển sang máy khác chỉ chạy server; chưa triển khai hoặc thay đổi dịch vụ.

## Thực hiện
Đã kiểm tra README/MAP/SPEC/PLAN, plugin bật, Git, `run.py`, `.gitignore`, script khởi động và cài Hermes. Repo công khai, nhánh hiện tại còn nhiều thay đổi chưa commit và chưa có `.github/workflows`. Dashboard dùng Flask development server; Hermes/9Router và tác vụ đăng nhập Windows được cài ngoài Git. `data/` chứa SQLite, ảnh và dấu sở hữu cron, còn token nằm trong biến môi trường User. Đã đối chiếu tài liệu chính thức GitHub Actions, GitHub Releases, Tailscale, Microsoft OpenSSH/Task Scheduler và Flask.

## Quyết định
Khuyến nghị CI trên GitHub-hosted Windows runner, rồi máy Windows đích tự kéo bản phát hành đã duyệt và chạy script cập nhật có backup/health-check/rollback. Cách này không cần cài self-hosted runner cho repo công khai và không cần mở cổng từ internet vào máy đích. Hai phương án thay thế là cập nhật thủ công bằng script hoặc GitHub Actions kết nối qua Tailscale + Windows OpenSSH. Không chọn phương án triển khai thay người dùng ở bước khảo sát.

## Kiểm chứng
Đối chiếu source/script thực tế và `gh repo view` xác nhận `PUBLIC`, nhánh mặc định `main`; `rg --files .github` xác nhận chưa có workflow. Không chạy test vì không đổi code hoặc lịch vận hành.

## Còn lại
Cần chốt hệ điều hành máy đích, nhịp cập nhật (tự động hay bấm duyệt), cách truy cập dashboard, di chuyển hoặc khởi tạo dữ liệu, và ngừng cron trên máy phát triển trước khi bật máy đích. Cần triển khai script bootstrap/deploy, health-check, backup và CI sau khi chọn phương án.
