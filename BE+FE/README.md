# VinUni AI Study Assistant

Đây là ứng dụng trợ lý học tập AI phong cách NotebookLM, hỗ trợ hỏi đáp và tra cứu kiến thức liên bài giảng từ các file slide PDF.

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

### 1. Chuẩn bị môi trường và thư viện
Đảm bảo bạn đã cài đặt Python (khuyên dùng 3.9 trở lên). Mở terminal tại thư mục dự án và chạy lệnh sau để cài đặt các thư viện cần thiết:

```bash
pip install streamlit PyMuPDF chromadb python-dotenv google-genai openai
```

### 2. Thêm file Slide (PDF)
Bạn hãy copy các file bài giảng PDF (ví dụ: `day2.pdf`, `day3.pdf`, `day4.pdf`...) và đặt vào thư mục `slide/` trong dự án. Cấu trúc thư mục sẽ trông như sau:

```text
publish_data/
├── slide/
│   ├── day2.pdf
│   ├── day3.pdf
│   └── ...
├── app.py
├── index_all_lectures.py
└── ...
```

*(Lưu ý: Mã nguồn mặc định đã được thiết lập để tự động đọc các file từ thư mục `slide/`).*

### 3. Nạp dữ liệu vào cơ sở dữ liệu (ChromaDB)
Để AI có thể tìm kiếm nội dung, bạn cần trích xuất text từ PDF và đưa vào Vector Database. Chạy lệnh sau trong terminal:

```bash
python index_all_lectures.py
```
*Hệ thống sẽ phân tích các file PDF trong thư mục `slide/` và tạo ra thư mục `chroma_db/` chứa cơ sở dữ liệu.*

### 4. Thiết lập API Key
Bạn có thể cung cấp API Key (Gemini hoặc OpenRouter) theo 1 trong 2 cách:
- **Cách 1 (Khuyên dùng):** Tạo một file có tên `.env` ở thư mục gốc dự án và điền mã của bạn vào:
  ```env
  GEMINI_API_KEY=your_gemini_api_key_here
  OPENROUTER_API_KEY=your_openrouter_api_key_here
  ```
- **Cách 2:** Bỏ qua bước tạo file `.env` và dán trực tiếp API Key vào khung nhập liệu trên thanh công cụ (Sidebar) khi mở ứng dụng.

### 5. Khởi chạy Ứng dụng
Cuối cùng, mở giao diện người dùng bằng lệnh:

```bash
streamlit run app.py
```
Trình duyệt sẽ tự động khởi động và mở trang web tại địa chỉ: `http://localhost:8501`.

---

## 🛠 Tùy chỉnh: Làm sao để thêm bài giảng mới?
Mặc định ứng dụng cấu hình sẵn các bài từ Day 2 đến Day 6. Nếu bạn muốn thêm một slide mới (VD: `day7.pdf`), hãy làm như sau:
1. Đặt file `day7.pdf` vào thư mục `slide/`.
2. Mở file `app.py` và `index_all_lectures.py`, tìm mảng `DEFAULT_LECTURES` ở phần đầu file và copy/paste thêm 1 khối thông tin cho bài mới. Ví dụ:
   ```python
    {
        "name": "Day 7: Chủ đề mới",
        "file": "day7.pdf",
        "path": "./slide/day7.pdf"
    }
   ```
3. Chạy lại lệnh `python index_all_lectures.py` ở terminal để nạp bài mới vào CSDL.
4. Refresh lại trình duyệt web để xem kết quả.
