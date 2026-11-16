# Trạng thái dự án

## Đã hoàn thành

- Bộ sinh 6.500 lịch hẹn mô phỏng, tái tạo được bằng hạt giống cố định.
- Kiểm tra chất lượng từng dòng và các quy tắc vận hành rõ ràng.
- Kho SQLite dạng sao với chiều ngày, chiều chuyên khoa và view báo cáo.
- Đối soát số dòng nguồn, bảng sự kiện, view và khóa ngoại mồ côi.
- Truy vấn SQL cho xu hướng tháng, phân phối chờ, lát cắt áp lực và nhắc hẹn.
- Dashboard tiếng Việt có bộ lọc, KPI, xu hướng, bản đồ nhiệt và kiểm soát dữ liệu.
- Báo cáo quyết định có đề xuất, giới hạn và khoảng Wilson.
- Kiểm tra tự động bằng Ruff, pytest và GitHub Actions.
- Tự tạo hoặc nâng cấp dữ liệu demo khi chạy trên máy mới.

## Mốc tham chiếu đã xác minh

- Tổng lịch hẹn: 6.500.
- Tỷ lệ vắng hẹn: 13,79%.
- Chờ trung vị: 27,7 phút.
- Chờ P90: 43,9 phút.
- Chuyên khoa có P90 cao nhất: Tim mạch, 50,5 phút.

## Bước tiếp theo an toàn

1. Triển khai `dashboard.py` lên Streamlit Community Cloud và bổ sung đường dẫn vào `README.md`.
2. Thêm ảnh chụp dashboard sau khi bản triển khai được kiểm tra trên màn hình laptop.
3. Thử độ nhạy với ngưỡng số mẫu của lát cắt, không thay đổi định nghĩa KPI chính.

Không thêm machine learning vào repository này. Phần đó thuộc đồ án AI Systems riêng để mỗi dự án giữ được câu chuyện tuyển dụng rõ ràng.
