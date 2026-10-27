# Kiểm tra sandbox hiện có của dự án

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Xác định repo hiện đã có môi trường sandbox cho CI/CD hay chưa; chỉ khảo sát.

## Thực hiện
Kiểm tra file workflow, Docker/staging, test và cờ lịch thử nghiệm trong source ứng dụng. Repo có `tests/` và cờ `test_only` để lịch thử nghiệm không đăng Facebook. Không thấy workflow của ứng dụng trong `.github/workflows` hay môi trường staging/sandbox triển khai; các file mang tên sandbox thuộc source Hermes vendored, không phải sandbox CI/CD của ứng dụng.

## Quyết định
Phân biệt test cục bộ và lịch thử nghiệm với môi trường CI tách biệt. Chưa tạo mới hạ tầng khi người dùng chỉ hỏi trạng thái.

## Kiểm chứng
Đọc kết quả `rg --files` và `rg -n` với các đường `.github`, test, sandbox/staging và `test_only`; không chạy test vì không sửa code.

## Còn lại
Cần xây GitHub Actions CI và bước thử bản mới tách dữ liệu/token thật khi triển khai CI/CD.
