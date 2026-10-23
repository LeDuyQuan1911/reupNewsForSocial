# Plugin: Security review

Khi plugin này bật, đánh giá rủi ro phù hợp với chức năng đang xây: dữ liệu nhạy cảm, đầu vào không tin cậy, xác thực/phân quyền, phụ thuộc và quyền truy cập hạ tầng.

- Ghi các rủi ro có căn cứ và biện pháp vào `contexte/decisions.md` hoặc tài liệu bảo mật riêng khi nội dung đủ lớn.
- Kiểm tra secrets trong thay đổi, xác thực đầu vào và quyền truy cập ở các đường đi liên quan.
- Dùng công cụ quét phụ thuộc hoặc cấu hình khi stack đã rõ; báo kết quả và giới hạn của lần quét.
- Không đổi quyền truy cập, xoay khóa hoặc công khai tài nguyên chỉ vì plugin đang bật.

Đầu ra là nhận xét có bằng chứng, sửa lỗi trong phạm vi nhiệm vụ và rủi ro còn lại. Plugin này bổ sung cho quy tắc secrets cơ bản, không thay thế chúng.
