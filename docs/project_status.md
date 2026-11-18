# Trạng thái dự án

## Đã hoàn thành

- Bộ sinh 6.500 lịch hẹn mô phỏng, tái tạo được bằng hạt giống cố định.
- Kiểm tra chất lượng từng dòng và các quy tắc vận hành rõ ràng.
- Kho SQLite dạng sao với chiều ngày, chiều chuyên khoa và view báo cáo.
- Đối soát số dòng nguồn, bảng sự kiện, view và khóa ngoại mồ côi.
- Truy vấn SQL cho xu hướng tháng, phân phối chờ, lát cắt áp lực và nhắc hẹn.
- Phân rã thời gian chờ thành tiếp nhận, chờ vào phòng và chờ bắt đầu khám.
- Phân tích độ nhạy ở ngưỡng 30, 50 và 70 lượt; biểu đồ p với giới hạn ba sigma.
- Bản tóm tắt stakeholder và sổ đăng ký giả định để phân biệt mô phỏng với bằng chứng thực tế.
- Dashboard tiếng Việt có bộ lọc, KPI, xu hướng, bản đồ nhiệt và kiểm soát dữ liệu.
- Website GitHub Pages tiếng Việt, tải nhanh và không cần đăng nhập; bộ lọc chạy trực tiếp trên trình duyệt.
- Dữ liệu JSON công khai tối thiểu, không chứa mã người bệnh, được tạo lại bằng mã nguồn và kiểm thử.
- Báo cáo quyết định có đề xuất, giới hạn và khoảng Wilson.
- Kiểm tra tự động bằng Ruff, pytest và GitHub Actions.
- Tự tạo hoặc nâng cấp dữ liệu demo khi chạy trên máy mới.
- Báo cáo chất lượng dữ liệu dạng JSON để CI và công cụ khác có thể đọc trực tiếp.

## Mốc tham chiếu đã xác minh

- Tổng lịch hẹn: 6.500.
- Tỷ lệ vắng hẹn: 13,79%.
- Chờ trung vị: 27,7 phút.
- Chờ P90: 43,9 phút.
- Chuyên khoa có P90 cao nhất: Tim mạch, 50,5 phút.
- Công đoạn lớn nhất tại Tim mạch: chờ bắt đầu khám, trung bình 20,8 phút.
- Cả ba ngưỡng cỡ mẫu đều xếp Tim mạch 09:00, 10:00 và 14:00 ở ba vị trí đầu.
- Không có tháng vượt giới hạn kiểm soát tỷ lệ vắng hẹn.

## Bước tiếp theo an toàn

1. Thêm ảnh chụp website sau khi bản GitHub Pages được kiểm tra trên màn hình laptop.
2. Thử độ nhạy với ngưỡng số mẫu của lát cắt, không thay đổi định nghĩa KPI chính.
3. Bổ sung chú thích sự kiện vận hành nếu có bộ dữ liệu thực tế phù hợp và đã được ẩn danh.

Không thêm machine learning vào repository này. Phần đó thuộc đồ án AI Systems riêng để mỗi dự án giữ được câu chuyện tuyển dụng rõ ràng.
