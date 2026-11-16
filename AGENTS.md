# Hướng dẫn tiếp tục dự án cho Codex

## Mục đích

Đây là đồ án portfolio Data Analyst về vận hành ngoại trú mô phỏng tại Buôn Ma Thuột. Giữ trọng tâm ở SQL, chất lượng dữ liệu, định nghĩa KPI, phân tích vận hành và trình bày trên dashboard. Mô hình dự đoán và triển khai AI thuộc repository AI Systems riêng.

## Dữ liệu và cách diễn giải

- Mọi lịch hẹn và mã người bệnh đều là dữ liệu mô phỏng.
- Không mô tả phát hiện như kết quả của một bệnh viện thật.
- Không thêm tên, số điện thoại, địa chỉ, bệnh án hoặc dữ liệu cá nhân.
- So sánh nhắc hẹn là liên hệ mô tả, không phải ước lượng nhân quả.
- Giữ nguyên định nghĩa trong `docs/metrics.md`, trừ khi cập nhật đồng bộ báo cáo, SQL và kiểm thử.
- Nội dung dành cho nhà tuyển dụng và giao diện phải viết bằng tiếng Việt rõ ràng, tự nhiên.

## Kiểm tra chuẩn trước khi commit

```powershell
ruff check .
ruff format --check .
pytest
python run_analysis.py
```

Khi thay đổi bộ sinh dữ liệu, KPI hoặc SQL, phải đối chiếu lại `reports/analysis_report.md` và các số tham chiếu trong `README.md`.

## Vệ sinh repository

- Không commit `.venv`, CSV/SQLite tạo sinh, kết quả truy vấn hoặc thông tin bí mật.
- Giữ `main` ở trạng thái chạy được; thay đổi lớn nên dùng nhánh ngắn hạn.
- Commit nhỏ, thông điệp nêu rõ kết quả phân tích hoặc kỹ thuật.
- Thêm kiểm thử khi bổ sung quy tắc dữ liệu, bảng kho, KPI hoặc truy vấn nghiệp vụ.

## Điểm vào quan trọng

- `run_analysis.py`: chạy toàn bộ quy trình có thể tái tạo.
- `dashboard.py`: demo Streamlit; tự tạo hoặc nâng cấp dữ liệu mẫu.
- `sql/analysis.sql`: các truy vấn nghiệp vụ có tên.
- `reports/analysis_report.md`: báo cáo quyết định dành cho nhà tuyển dụng.
- `docs/project_status.md`: trạng thái hiện tại và bước tiếp theo an toàn.
