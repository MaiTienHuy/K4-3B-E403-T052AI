# BÁO CÁO THU HOẠCH CÁ NHÂN (PERSONAL REFLECTION)

- **Họ và tên:** Hoàng Ngọc Đức
- **Nhóm:** T52AI
- **Vai trò đảm nhiệm:** Data Pipeline (PDF → JSON → Vector), Giao diện tương tác (Streamlit UI) & Hạ tầng triển khai Self-host (Docker, Nginx, Cloudflare Tunnel)

---

## 1. VAI TRÒ CÁ NHÂN & PHẦN VIỆC TRỰC TIẾP PHỤ TRÁCH

Trong dự án VLearn Course Navigator, tôi đảm nhiệm các phần việc xây dựng nền tảng dữ liệu ban đầu, phát triển giao diện tương tác người dùng và toàn bộ khâu đóng gói triển khai (deployment). Chi tiết các phần việc trực tiếp phụ trách:

### 1.1. Xây dựng Pipeline Dữ liệu: PDF → JSON → Vector & Base Query
- **Trích xuất & Cấu trúc hóa Dữ liệu (PDF → JSON):**
  - Xử lý các tệp tài liệu slide bài giảng gốc (từ Day 1 đến Day 6).
  - Viết pipeline bóc tách nội dung thô từ file PDF thành định dạng JSON chuẩn hóa (`dayX_rag.json`).
  - Gắn metadata chi tiết cho từng khối dữ liệu: định danh buổi học (`lecture_id`), số thứ tự trang/slide (`slide_number`), tiêu đề trang và nội dung văn bản. Việc này đảm bảo tính toàn vẹn để mọi trích dẫn sau này đều ánh xạ ngược được về đúng trang slide gốc.
- **Tạo Embedding & Xây dựng Cơ chế Query Vector ban đầu:**
  - Thiết lập mô hình embedding để chuyển đổi toàn bộ nội dung văn bản trong các file JSON thành các vector đặc trưng.
  - Lưu trữ vào Vector Database (ChromaDB) và viết các hàm truy vấn tìm kiếm tương đồng (similarity search) dựa trên độ đo khoảng cách (cosine similarity), làm tiền đề cho hệ thống truy hồi thông tin (Retrieval).
  *(Lưu ý: Tầng phân loại chủ đích routing, decision layer và module mở rộng sau này do thành viên khác phụ trách phát triển nâng cao).*

### 1.2. Phát triển Giao diện Tương tác Người dùng (Streamlit Frontend - `app.py`)
- **Thiết kế Bố cục Đồng bộ 2 Cột (Split-Screen):**
  - **Cột bên trái (Slide Viewer):** Tích hợp trình hiển thị slide trực quan, cho phép học viên lật mở từng trang bài giảng theo đúng tài liệu thực tế của buổi học đang mở.
  - **Cột bên phải (Chat Tutor):** Khung chat tương tác với trợ lý ảo, hiển thị phản hồi của AI cùng các trích dẫn nguồn gốc tương ứng.
- **Xây dựng Tính năng Deep Linking (Nhảy trang 1 chạm):**
  - Xử lý logic liên kết giữa câu trả lời của bot và trình xem bài giảng: khi câu trả lời có nguồn trích dẫn (ví dụ: `[REF:day4.pdf:12]`), giao diện sinh nút điều hướng tương ứng. Khi học viên click vào nút, hệ thống cập nhật `st.session_state` để khung slide bên trái tự động nhảy ngay đến trang đó.
- **Cải tiến UX/UI Dựa trên Phản hồi Kiểm thử Thực tế (User Testing):**
  - Sửa lỗi ghim cuộn (sticky layout) để khung slide hiển thị ổn định, không bị che khuất khi người dùng cuộn xem lịch sử chat.
  - Tối ưu luồng chuyển bài: không tự ý ép chuyển bài khi học viên chưa bấm duyệt (tránh gây mất dấu bài học hiện tại).

### 1.3. Đóng gói & Triển khai Hạ tầng Self-host (DevOps & Deployment)
- **Container hóa với Docker:** Thiết lập `Dockerfile` và `docker-compose.yml`, đóng gói toàn bộ môi trường Python cùng các thư viện cần thiết để ứng dụng có thể khởi chạy nhất quán ở bất kỳ đâu.
- **Thiết lập Reverse Proxy với Nginx:** Cấu hình file `nginx.conf` với đầy đủ hỗ trợ cho giao thức WebSocket của Streamlit (`Upgrade`, `Connection "upgrade"`), thiết lập bộ đệm và cấu hình Rate Limiting (`limit_req_zone`) nhằm ngăn chặn việc spam request làm quá tải hệ thống.
- **Công khai Dịch vụ an toàn bằng Cloudflare Tunnel:** Cấu hình Cloudflare Tunnel kết nối từ máy chủ local ra ngoài Internet. Giải pháp này giúp người dùng ngoài nhóm có thể truy cập kiểm thử qua domain HTTPS bảo mật mà không cần mở cổng modem (NAT port forwarding) hay lộ địa chỉ IP thật.
- **Cơ chế Hot-reloading:** Cấu hình volume mounting (`- .:/app`) trong Docker Compose giúp cập nhật mã nguồn ngay lập tức trong quá trình phát triển mà không phải mất thời gian build lại container.

---

## 2. CÁCH ỨNG DỤNG AI TRONG QUÁ TRÌNH XÂY DỰNG

Tôi đã tận dụng triệt để các công cụ AI (như Claude Code, Antigravity) với vai trò một "trợ lý lập trình cặp" (AI Pair Programmer) để nâng cao năng suất và chất lượng công việc:

1. **Hỗ trợ xử lý & làm sạch dữ liệu PDF (AI-assisted Data Parsing):**
   - Khi parse PDF slide dạng thô, chữ thường bị dính liền hoặc lộn xộn thứ tự do layout nhiều cột. Tôi đã sử dụng AI để hỗ trợ viết các script regex và tiền xử lý văn bản, giúp chuẩn hóa dữ liệu đầu ra JSON sạch, giữ nguyên số trang và ngữ cảnh từng slide.

2. **Tăng tốc cấu hình Hạ tầng & DevOps:**
   - Sử dụng AI để sinh nhanh các mẫu cấu hình chuẩn của Nginx cho Streamlit (vốn rất hay gặp lỗi `403` hoặc rớt kết nối WebSocket nếu không cấu hình đúng header).
   - Tham khảo AI để tối ưu kích thước Docker image và viết kịch bản tự động hóa kiểm tra trạng thái dịch vụ.

3. **Gỡ lỗi & Tối ưu giao diện Streamlit:**
   - Streamlit có cơ chế re-run toàn bộ trang mỗi khi có sự kiện click, gây khó khăn cho việc duy trì trạng thái xem slide và thanh cuộn. Tôi đã ứng dụng AI để phân tích cơ chế quản lý state (`st.session_state`), từ đó tìm ra cách lưu vị trí trang hiện tại và xử lý CSS tùy biến cho thanh cuộn giao diện một cách mượt mà.

---

## 3. BÀI HỌC THỰC TẾ RÚT RA TỪ CHÍNH CÁC TRƯỜNG HỢP THẤT BẠI CỦA NHÓM

Trong quá trình phối hợp nhóm và triển khai sản phẩm, chúng tôi đã gặp phải những thất bại thực tế rất rõ ràng, mang lại những bài học kinh nghiệm sâu sắc:

### Thất bại 1: Thất bại của Naive Vector Search thuần túy dẫn đến sai lệch câu trả lời
- **Trường hợp thất bại:** Ở giai đoạn đầu, tôi xây dựng phần truy vấn hoàn toàn dựa trên việc so khớp độ tương đồng vector (Vector Similarity / Naive RAG) giữa câu hỏi của học viên và các đoạn văn bản trong cơ sở dữ liệu. Khi nhóm tiến hành chạy kiểm thử với bộ dữ liệu thực tế (Golden Set), hệ thống bộc lộ lỗi nghiêm trọng:
  - Khi học viên đang ở bài 5 nhưng hỏi *"ôn lại bài 1"*, vector search thuần túy lại trả về các slide của bài 3 hoặc bài 4 chỉ vì trong các bài đó giảng viên có nhắc lại từ "ôn tập" hoặc "bài 1".
  - Khi học viên hỏi một khái niệm xuất hiện ở nhiều buổi (như *RAG* hay *Evaluation*), mô hình tự ý bốc đại slide có điểm tương đồng cao nhất để trả lời thay vì hỏi lại để làm rõ ý người học.
- **Bài học rút ra:** **Không thể phó mặc trải nghiệm người dùng cho một mình Vector Database.** Một pipeline RAG hiệu quả trong thực tế bắt buộc phải có sự tách bạch:
  - Tầng dữ liệu vector chỉ đóng vai trò kho lưu trữ và tra cứu nội dung chi tiết.
  - Cần phải có **Tầng phân định chủ đích (Decision / Intent Layer)** đứng trước để phân tích cấu trúc câu hỏi, xác định ngữ cảnh buổi học hiện tại (`anchor lecture`), từ đó mới quyết định chiến lược tìm kiếm hoặc yêu cầu người dùng làm rõ trước khi query vector.

### Thất bại 2: Container bị OOM Crash khi deploy lên Cloud miễn phí (Render)
- **Trường hợp thất bại:** Nhóm từng thử nghiệm đưa ứng dụng lên các nền tảng PaaS miễn phí (như Render free tier). Tuy nhiên, giới hạn 512MB RAM của gói miễn phí không thể gánh nổi đồng thời: runtime Python, ứng dụng Streamlit, bộ thư viện Vector DB và quá trình tải model embedding vào bộ nhớ. Kết quả là container liên tục bị hệ thống kill do vượt ngưỡng RAM (`Exit Code 137 / OOM`), cộng thêm việc dữ liệu vector bị mất sạch sau mỗi lần restart do không có ổ cứng lưu trữ bền vững (persistent storage).
- **Bài học rút ra:** **Cần chủ động tính toán tài nguyên thực tế cho các ứng dụng có thành phần AI/Vector.** Đừng phụ thuộc vào cloud free-tier có cấu hình quá yếu. Việc tôi chuyển đổi kịp thời sang giải pháp **Self-host trên máy vật lý kết hợp Docker + Nginx + Cloudflare Tunnel** đã giải phóng hoàn toàn giới hạn phần cứng, đảm bảo hệ thống duy trì thời gian hoạt động ổn định 100% để phục vụ người dùng thử nghiệm với chi phí 0 đồng.

### Thất bại 3: Lỗi đứt mạch học tập khi tự động can thiệp vào giao diện người dùng
- **Trường hợp thất bại:** Ban đầu trên giao diện, tôi thiết kế tính năng khi chatbot nhận diện thấy câu hỏi thuộc về buổi học khác, hệ thống sẽ tự động chuyển luôn slide viewer sang buổi đó. Tuy nhiên, khi đưa cho người dùng ngoài nhóm kiểm thử (phiên của bạn Nguyễn Thái Lương), học viên phản hồi tiêu cực: *"Đừng tự chuyển trang dùm — mình chỉ muốn đọc nhanh câu trả lời rồi tiếp tục bài đang học"*. Việc hệ thống tự ý nhảy trang đã khiến học viên bị mất dấu vị trí bài giảng đang theo dõi.
- **Bài học rút ra:** **AI chỉ nên đóng vai trò gợi ý và hỗ trợ, quyền quyết định chuyển đổi ngữ cảnh phải luôn thuộc về người dùng.** Tôi đã điều chỉnh lại giao diện: chatbot chỉ hiển thị nút nguồn tham khảo rõ ràng (CTA) và chỉ khi học viên chủ động bấm vào nút đó thì slide mới được điều hướng đến trang tương ứng.

---

## 4. TỔNG KẾT

Qua dự án này, từ khâu xử lý dữ liệu thô ban đầu, xây dựng giao diện tương tác cho đến khi tự tay dựng hạ tầng self-host đưa sản phẩm ra môi trường thực tế, tôi đã học được cách làm việc chặt chẽ với các thành viên khác trong nhóm. Thất bại từ cách tiếp cận vector search đơn giản ban đầu hay sự cố sập hạ tầng trên cloud chính là những trải nghiệm thực tế quý giá giúp tôi hiểu sâu hơn về kiến trúc của một hệ thống RAG hoàn chỉnh trong đời thực.
