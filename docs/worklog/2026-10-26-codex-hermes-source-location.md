# Vị trí mã nguồn Hermes

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích vì sao repo ứng dụng không chứa mã nguồn Hermes và xác định nơi mã nguồn open source đã được cài trên máy.

## Thực hiện
Kiểm tra remote của repo ứng dụng và thư mục mã nguồn Hermes do installer tạo. Chỉ thêm nhật ký này; không sửa mã ứng dụng.

## Quyết định
Giữ Hermes như một công cụ cài riêng ngoài repo ứng dụng để không trộn mã của hai dự án.

## Kiểm chứng
Remote repo ứng dụng trỏ đến `LeDuyQuan1911/reupNewsForSocial`; checkout Hermes trỏ đến `NousResearch/hermes-agent`, có `hermes_cli/main.py` và tag `v0.22.5`.

## Còn lại
Không có.
