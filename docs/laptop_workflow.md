# Tiếp tục dự án trên máy tính khác

GitHub là nguồn mã dùng chung. CSV, SQLite và kết quả truy vấn được chủ động loại khỏi Git vì mỗi máy có thể tạo lại chính xác từ cùng mã nguồn và hạt giống ngẫu nhiên.

## Mở dự án bằng Codex trên laptop

1. Cài ứng dụng ChatGPT có Codex và đăng nhập cùng tài khoản.
2. Clone repository bằng các lệnh bên dưới.
3. Trong Codex, mở thư mục `outpatient-operations-analysis` làm thư mục dự án.
4. Tạo chat mới và yêu cầu: `Đọc AGENTS.md và docs/project_status.md, sau đó tiếp tục bước an toàn tiếp theo.`

Lịch sử chat không tự sao chép thư mục mã nguồn giữa hai máy. Repository lưu bối cảnh bền vững để Codex hoặc người phát triển khác có thể tiếp tục đúng chỗ.

## Thiết lập lần đầu

```powershell
git clone https://github.com/khanhnguyenpham/outpatient-operations-analysis.git
cd outpatient-operations-analysis
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python run_analysis.py
streamlit run dashboard.py
```

## Bắt đầu một thay đổi

Cập nhật `main` trước khi tạo nhánh ngắn hạn:

```powershell
git switch main
git pull --ff-only
git switch -c feature/mo-ta-ngan
```

Sau khi sửa, chạy cùng các kiểm tra với GitHub Actions:

```powershell
ruff check .
ruff format --check .
pytest
python run_analysis.py
```

Commit và đẩy nhánh:

```powershell
git add .
git commit -m "Mô tả kết quả thay đổi"
git push -u origin feature/mo-ta-ngan
```

Chỉ hợp nhất khi kiểm tra tự động đạt. Trên máy còn lại, quay về `main` và chạy `git pull --ff-only` trước khi tiếp tục.

## Tệp chỉ nên nằm trên máy cá nhân

- `.venv/`
- CSV và SQLite trong `data/generated/`
- kết quả truy vấn trong `reports/generated/`
- cấu hình bí mật của Streamlit

Không đưa token, mật khẩu hoặc `.streamlit/secrets.toml` lên Git.
