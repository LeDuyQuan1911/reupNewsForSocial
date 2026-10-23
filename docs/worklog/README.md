# Nhật ký công việc

Mỗi yêu cầu liên quan đến repo cần một file riêng tại đây, kể cả nhiệm vụ chỉ khảo sát hoặc review. Tạo file khi bắt đầu, bổ sung kết quả trước khi bàn giao. Quy tắc này luôn có hiệu lực, không phụ thuộc plugin `documentation`.

Tên file: `YYYY-MM-DD-<agent>-<task>.md`. Dùng tên nhiệm vụ ngắn, chữ thường, dấu gạch ngang. Nếu trùng tên, thêm số hoặc mã nhiệm vụ. Mỗi agent chỉ sửa log của nhiệm vụ mình trong worktree riêng.

## Nội dung tối thiểu

```markdown
# <Tên nhiệm vụ>

- Ngày: YYYY-MM-DD
- Agent: Codex | Antigravity | Claude Code | ...
- Trạng thái: đang làm | hoàn tất | bị chặn

## Yêu cầu và phạm vi
Người dùng muốn gì; phần nào được làm.

## Thực hiện
Các thay đổi hoặc hoạt động khảo sát, file liên quan và lý do.

## Quyết định
Các lựa chọn quan trọng và căn cứ; nếu không có, ghi "Không có".

## Kiểm chứng
Lệnh hoặc cách kiểm tra, kết quả; nếu không chạy được, ghi rõ lý do.

## Còn lại
Giới hạn, rủi ro hoặc bước tiếp theo; nếu không có, ghi "Không có".
```

Không ghi secrets, dữ liệu nhạy cảm hoặc toàn bộ log đầu ra chứa thông tin riêng tư. Worklog ghi lại bằng chứng và kết quả ngắn gọn; quyết định lâu dài vẫn được đưa vào `contexte/decisions.md`, yêu cầu vào `SPEC.md`, trạng thái kế hoạch vào `PLAN.md`.

Trước khi bàn giao, chạy `node scripts/check-worklog.mjs <tên-file.md>`. Lệnh kiểm tra trạng thái hoàn tất và các mục bắt buộc. `node scripts/check-worklog.mjs --all` kiểm tra toàn bộ nhật ký.
