# 🎓 VLearn Study Assistant

> Trợ lý học tập AI thông minh dành riêng cho học viên VinUni (môn AI Product). Ứng dụng mang phong cách NotebookLM, hỗ trợ hỏi đáp, tra cứu kiến thức và điều hướng liên bài giảng (Cross-lecture Navigation) từ các file slide PDF.

---

## ✨ Tính Năng Nổi Bật

- 🤖 **Trợ lý Thông Minh:** Sử dụng LLM tiên tiến (Gemini / OpenRouter - DeepSeek) để giải đáp thắc mắc.
- 📚 **Truy Xuất Kiến Thức (RAG):** Tìm kiếm thông tin chính xác từ hàng loạt slide PDF (Day 2 - Day 6, v.v.).
- 🗺️ **Định Tuyến Liên Bài Giảng (Cross-lecture Navigation):** Tự động phát hiện nếu câu hỏi thuộc phạm vi bài học khác và hướng dẫn người dùng tới đúng bài.
- 🔗 **Trích Dẫn Nguồn Minh Bạch:** Mọi câu trả lời đều được gắn thẻ `[REF:file:page]` để người học dễ dàng đối chiếu trực tiếp.
- 🛡️ **Bảo Vệ Học Thuật (Guardrails):** Không giải hộ bài tập chấm điểm, kháng prompt injection và cam kết 0% bịa đặt (hallucination).

---

## 🛠 Công Nghệ Sử Dụng (Tech Stack)

- **Giao diện (Frontend):** [Streamlit](https://streamlit.io/)
- **Cơ sở dữ liệu Vector:** [ChromaDB](https://www.trychroma.com/)
- **Xử lý PDF:** [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **LLM APIs:** Google Gemini SDK, OpenAI SDK (OpenRouter)

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 1. Chuẩn bị môi trường
Đảm bảo bạn đã cài đặt Python (khuyến nghị 3.9+). Clone hoặc tải dự án về máy, sau đó mở terminal và cài đặt các thư viện cần thiết:

```bash
pip install streamlit PyMuPDF chromadb python-dotenv google-genai openai
```

### 2. Cấu trúc dữ liệu bài giảng
Các file slide (`.pdf`) cần được đặt trong thư mục `slide/`. Cấu trúc dự án sẽ trông như sau:

```text
BE+FE/
├── slide/
│   ├── day2.pdf
│   ├── day3.pdf
│   └── ...
├── app.py
├── index_all_lectures.py
└── ...
```

### 3. Khởi tạo Cơ Sở Dữ Liệu (ChromaDB)
Để AI có thể tìm kiếm và truy xuất thông tin, bạn cần nạp (index) text từ file PDF vào Vector Database. Chạy lệnh sau:

```bash
python index_all_lectures.py
```
*(Lệnh này sẽ tạo ra một thư mục `chroma_db/` chứa CSDL).*

### 4. Cấu Hình API Key
Ứng dụng hỗ trợ Gemini và các mô hình qua OpenRouter (như DeepSeek). 
Tạo một file `.env` tại thư mục `BE+FE` (cùng cấp với `app.py`) và thêm API keys của bạn:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```
*(Ngoài ra, bạn cũng có thể nhập API Key trực tiếp trên giao diện Sidebar của ứng dụng).*

### 5. Khởi chạy App
Mở terminal và gõ lệnh:

```bash
streamlit run app.py
```
Giao diện web sẽ tự động bật lên tại: `http://localhost:8501`.

---

## 🐳 Hướng Dẫn Triển Khai (Docker & Tunnels)

Để xem hướng dẫn chi tiết cách tự deploy miễn phí ứng dụng bằng Docker, Nginx và Cloudflare Tunnels (khắc phục giới hạn của Render, chống DDoS/Spam), vui lòng xem file [DEPLOYMENT.md](./DEPLOYMENT.md).

---

## 🧪 Công Cụ Đánh Giá (Evaluation)

Dự án cung cấp sẵn bộ công cụ đánh giá (Evaluation) để kiểm tra khả năng định tuyến (Routing) và độ chính xác của AI.

- Script đánh giá nằm tại: `eval/run_eval.py`
- Bộ câu hỏi test (Golden Set): `eval/golden_set_cross_lecture.json`

**Cách chạy đánh giá:**
```bash
python eval/run_eval.py            # Chạy toàn bộ test cases
python eval/run_eval.py --limit 3  # Chỉ chạy 3 case đầu tiên để test nhanh
```
Kết quả đánh giá chi tiết sẽ được xuất ra file `report_latest.json` và bảng tóm tắt tại `summary_latest.json`.

---

## ⚙️ Tùy Chỉnh: Thêm Bài Giảng Mới

Để thêm một bài giảng mới (VD: `day7.pdf`), hãy thực hiện các bước sau:
1. Copy file `day7.pdf` vào thư mục `slide/`.
2. Mở file `app.py` và `index_all_lectures.py`, tìm danh sách biến `DEFAULT_LECTURES` và bổ sung thêm bài học:
   ```python
   {
       "name": "Day 7: Tên Chủ Đề",
       "file": "day7.pdf",
       "path": "./slide/day7.pdf"
   }
   ```
3. Chạy lại lệnh `python index_all_lectures.py` để cập nhật ChromaDB.
4. Refresh lại trình duyệt (app Streamlit) để trải nghiệm.
