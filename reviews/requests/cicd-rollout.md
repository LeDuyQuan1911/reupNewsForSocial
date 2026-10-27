# Yêu cầu review: cicd-rollout

- Base commit: `6f578cec842e8db3b6cbc533bdb6bc27809dfc50`
- Head commit: `2e410a845a60a86450086b06649e31b496a21541`
- Phạm vi: ứng dụng Flask/Hermes/Facebook, workflow `.github/workflows/ci.yml`, script `scripts/cd/`, các test và tài liệu có liên quan. `vendor/hermes-agent/` là snapshot upstream được đưa vào ở commit trước; kiểm tra thay đổi tích hợp quanh nó và rủi ro phát hành.
- Tiêu chí chấp nhận: `SPEC.md` và `docs/deployment.md`; PR và `main` chạy CI Windows không có secrets, server chỉ nhận đúng SHA `main` có CI push xanh, không làm mất DB/media/secrets, không tạo đăng bài trùng khi cập nhật hoặc phục hồi.
- Lệnh kiểm tra: `python -m unittest discover -s tests -q`, `python scripts/cd/smoke.py`, kiểm tra cú pháp PowerShell và `git diff --check`.
- Ngoài phạm vi: thao tác thật với Page/9Router hoặc cài máy server Windows.

## Prompt cho reviewer

Review độc lập diff giữa base và head. Đọc `AGENTS.md`, `plugins/independent-review/INSTRUCTIONS.md`, `reviews/README.md` và yêu cầu này. Ở lượt đầu chưa đọc worklog, PR description hoặc nhận xét của tác giả. Chỉ đọc code/chạy kiểm tra, không sửa implementation. Ghi báo cáo có bằng chứng theo `reviews/templates/REPORT.md` vào `reviews/reports/cicd-rollout.md`, tạo worklog riêng rồi commit báo cáo và worklog trên branch review. Báo lại hash commit.
