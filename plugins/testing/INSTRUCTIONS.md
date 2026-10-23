# Plugin: Testing

Khi plugin này bật, xác định các hành vi quan trọng từ `SPEC.md` rồi chọn mức kiểm thử phù hợp với stack và rủi ro. Không thêm framework kiểm thử trước khi biết công nghệ và đường chạy ứng dụng.

- Bổ sung test có khả năng phát hiện lỗi thực tế cho thay đổi hành vi.
- Giữ test lặp lại được, không phụ thuộc secrets hoặc dịch vụ production.
- Ghi lệnh chạy và điều kiện cần thiết trong `README.md` khi đã có source.
- Chạy test liên quan trước khi bàn giao; nêu rõ test nào chưa chạy và lý do.

Plugin hoàn thành cho một chức năng khi hành vi chính có kiểm chứng phù hợp và kết quả chạy được báo cáo.
