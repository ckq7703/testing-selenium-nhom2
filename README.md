# Testing Selenium - Nhóm 2

Hệ thống này cung cấp giao diện để quản lý và hiển thị danh sách các test case, đồng thời hỗ trợ chạy các bài kiểm thử tự động bằng Selenium và Pytest. Dưới đây là hướng dẫn chi tiết để thiết lập và sử dụng hệ thống.

## Yêu cầu hệ thống
- **Hệ điều hành**: Windows, macOS, hoặc Linux
- **Python**: Phiên bản 3.8 hoặc cao hơn
- **Git**: Đã cài đặt để clone repository
- **Trình duyệt**: Chrome hoặc Firefox (để chạy Selenium tests)
- **Virtualenv** (khuyến nghị): Để tạo môi trường ảo

## Hướng dẫn cài đặt và sử dụng

### 1. Tải source code từ GitHub
Clone repository về máy tính của bạn bằng lệnh sau:

```bash
git clone https://github.com/ckq7703/testing-selenium-nhom2.git
cd testing-selenium-nhom2
```

### 2. Tạo môi trường ảo
Tạo và kích hoạt môi trường ảo để cô lập các thư viện của dự án:

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate
```

Sau khi kích hoạt, bạn sẽ thấy tên môi trường ảo (ví dụ: `(venv)`) xuất hiện trong terminal.

### 3. Cài đặt các thư viện từ `requirements.txt`
Cài đặt các thư viện cần thiết cho dự án bằng lệnh:

```bash
pip install -r requirements.txt
```

File `requirements.txt` chứa các thư viện như `Flask`, `pytest`, `selenium`, và các phụ thuộc khác. Đảm bảo bạn đã ở trong thư mục dự án và môi trường ảo đã được kích hoạt.

### 4. Chạy test tự động với Pytest
Sử dụng Pytest để chạy các bài kiểm thử tự động và tạo báo cáo HTML:

```bash
pytest -v --html=report.html --self-contained-html
```

- **Giải thích**:
  - `-v`: Hiển thị chi tiết kết quả kiểm thử.
  - `--html=report.html`: Tạo file báo cáo HTML với tên `report.html` (bạn có thể thay đổi tên file này tùy ý, ví dụ: `test_report.html`).
  - `--self-contained-html`: Đảm bảo file HTML báo cáo độc lập, không phụ thuộc vào các file CSS/JS bên ngoài.

Sau khi chạy, file báo cáo (ví dụ: `report.html`) sẽ được tạo trong thư mục hiện tại. Mở file này bằng trình duyệt để xem kết quả kiểm thử.

### 5. Chạy ứng dụng Flask để xem giao diện danh sách test case
Chạy file `app.py` để khởi động ứng dụng web Flask, hiển thị giao diện danh sách các test case:

```bash
python app.py
```

- Sau khi chạy, truy cập vào địa chỉ `http://localhost:5000` (hoặc cổng khác nếu được cấu hình) trên trình duyệt để xem giao diện.
- Giao diện sẽ hiển thị danh sách các test case được load từ file JSON (ví dụ: `challenges.json`), như được định nghĩa trong template `datatables.html`.

## Lưu ý
- **File JSON**: Đảm bảo file `challenges.json` (hoặc file dữ liệu tương ứng) nằm trong thư mục `static/` và có định dạng đúng như sau:
  ```json
  [
    {
      "section": "Section 1",
      "desc": "TEST001",
      "title": "Challenge Title",
      "description": "Description of challenge",
      "guide": "Guide text",
      "points": 100,
      "public": "Yes",
      "expected": "Success"
    },
    ...
  ]
  ```
- **Trình duyệt cho Selenium**: Đảm bảo bạn đã cài đặt trình duyệt (Chrome hoặc Firefox) và driver tương ứng (`chromedriver` hoặc `geckodriver`) phù hợp với phiên bản trình duyệt. Các driver này cần được thêm vào biến môi trường `PATH` hoặc đặt trong thư mục dự án.
- **Tùy chỉnh cổng Flask**: Nếu cổng 5000 bị chiếm, bạn có thể chỉ định cổng khác khi chạy `app.py`:
  ```bash
  python app.py --port 5001
  ```
  (Cần chỉnh sửa `app.py` để hỗ trợ tham số `--port` nếu muốn.)

## Xử lý sự cố
- **Lỗi cài đặt thư viện**: Nếu gặp lỗi khi chạy `pip install -r requirements.txt`, hãy kiểm tra phiên bản Python (`python --version`) và đảm bảo môi trường ảo đang hoạt động.
- **Lỗi chạy test**: Nếu Pytest báo lỗi liên quan đến Selenium, hãy kiểm tra xem driver trình duyệt có được cài đặt đúng và tương thích với phiên bản trình duyệt hay không.
- **Lỗi chạy Flask**: Nếu không truy cập được `http://localhost:5000`, kiểm tra xem file `app.py` có lỗi cú pháp hoặc file `challenges.json` có tồn tại và đúng định dạng hay không.

## Đóng góp
Nếu bạn muốn đóng góp vào dự án, hãy:
1. Fork repository.
2. Tạo nhánh mới (`git checkout -b feature/ten-nhanh`).
3. Commit các thay đổi (`git commit -m 'Mô tả thay đổi'`).
4. Push nhánh (`git push origin feature/ten-nhanh`).
5. Tạo Pull Request trên GitHub.

## Liên hệ
Nếu có câu hỏi hoặc cần hỗ trợ, vui lòng mở issue trên GitHub hoặc liên hệ với nhóm phát triển.

---

© 2025 Nhóm 2
