# Phiên 02 — Trần Cao Quốc Định

| Trường | Giá trị |
|---|---|
| Thời điểm | 18/09/2026 · 19:35–19:48 |
| Vai | Học viên K4 · hay kẹt khi nối lý thuyết giữa các buổi |
| Willing user CP1? | Có |
| Ngoài nhóm? | Có — không thuộc 4 thành viên Nhóm 03 |
| Facilitator | Mai Tiến Huy |
| Prototype | `BE+FE/app.py` · mặc định Day 5 |
| Task chính | Đang học bài 5, tìm và ôn lại **ReAct** đã học ở buổi trước |
| Task khó thêm | Vì lượt 1 khá thuận: hỏi **attention**, rồi **RAG là gì** |
| Cứu hộ đã dùng | “Bạn nghĩ nó nên hoạt động thế nào?” (khi kẹt Day 1) |
| Thuyết minh màn hình? | Không |

---

## 1. Câu chuyện thật — trước khi mở prototype

**Câu hỏi:** Kể một tình huống thật từng gặp liên quan đến vấn đề sản phẩm giải quyết, trước khi được xem prototype.

**Trả lời nguyên văn:**

> Hôm làm lab Day 5 mình muốn đối chiếu ReAct ở Day 3 với cái ngưỡng tự động đang học. Mình hỏi “ReAct khác chatbot chỗ nào”. Tutor bảo không có trong bài hiện tại. Mình mở tab khác, tìm file slide Day 3 trong Drive nhóm, tải xuống, tìm chữ ReAct. Xong không chắc đó có phải trang thầy dạy không vì không có số trang gắn với câu trả lời. Mất khoảng một buổi tối chỉ để nối lại hai khái niệm.

**Hành vi / ngữ cảnh:** đã từng rời LMS, tìm file thủ công, thiếu citation trang.

---

## 2. Task đã giao

> Bạn đang học bài 5 nhưng muốn ôn lại kiến thức về ReAct đã học ở những buổi trước. Hãy sử dụng hệ thống để tìm và ôn lại nội dung đó.

Sau ~3 phút job ReAct khép, giao thêm (vì chưa đủ chỗ khó):

> Giờ hãy ôn lại attention mechanism, rồi hỏi RAG là gì — vẫn đang trong mạch bài 5.

---

## 3. Quan sát ~5 phút (tầng 1)

| Phút | Hành vi quan sát được |
|---|---|
| 0:30 | Gõ `ôn lại ReAct đã học buổi trước`. Không đụng dropdown. |
| 1:00 | Hệ thống trỏ Day 3, hiện nguồn. **Do dự ~8 giây**, mắt nhìn dropdown rồi nhìn nút nguồn. |
| 1:15 | Bấm nguồn Day 3. Cột trái nhảy đúng bài. Đọc slide, gật. Job 1 khép. |
| 2:00 | Gõ `attention mechanism là gì`. |
| 2:20 | Hệ thống báo thuộc Day 1, **không có trang nguồn**. Người thử dừng. Click dropdown tìm “Day 1” — **không có** trong danh sách (chỉ Day 2–6). |
| 2:40 | Lặp lại câu hỏi một lần. Cùng kết quả. Không tiến được. |
| 2:50 | Cứu hộ: “Bạn nghĩ nó nên hoạt động thế nào?” |
| 3:00 | Nói lúc dùng: “Nó biết là bài 1 rồi mà đứng. Ít ra cho mình hỏi cái khác còn slide, hoặc nói rõ bài 1 chưa nạp.” |
| 3:40 | Tự gõ `RAG là gì`. Hệ thống **không đoán** — hiện 3 lựa chọn Day 2 / 3 / 5. |
| 4:00 | Ngần ~12 giây, rồi bấm Day 3. Có câu trả lời + nguồn. Bấm nguồn. |
| 5:10 | Dừng. Không nói “mình sẽ dùng hàng ngày”. |

**Kết luận tầng 1:** Happy path ReAct chạy. Chỗ khó thật là Day 1 hết đường; G10 với RAG thì người thử chọn được sau một nhịp do dự.

---

## 4. Nói lúc dùng (tầng 2)

- “Nó biết là bài 1 rồi mà đứng.”
- “Ít ra cho mình hỏi cái khác còn slide, hoặc nói rõ bài 1 chưa nạp.”
- (Khi thấy 3 nút RAG) “À, nó bắt mình chọn buổi chứ không bịa.”

---

## 5. Năm câu — trả lời

### Câu A — Tình huống thật (trước prototype)

Xem mục 1. Đồng ý đúng pain: đang học bài mới, cần nối khái niệm bài cũ, tutor đẩy mình tự tìm, mất thời gian và mất căn cứ số trang.

### Câu B — Nhận task theo mục tiêu

Đã làm task ReAct từ Day 5; sau đó nhận task khó attention + RAG.

### Câu C — Tự dùng ~5 phút

Tự dùng. ReAct khép được. Attention không khép. RAG khép sau khi tự chọn buổi.

### Câu D — Nói suy nghĩ lúc dùng

Đã nói: hệ thống biết Day 1 nhưng đứng; muốn được chỉ bước tiếp; hiểu G10 là “bắt chọn buổi chứ không bịa”.

### Câu E — Sau khi dùng

**Chỗ kẹt:** “Hỏi attention là chết. Mình tìm Day 1 trong list không thấy. Còn lúc RAG nó đưa 3 nút thì mình hơi dừng vì không chắc chọn nút nào, nhưng còn làm tiếp được.”

**Kết quả có đúng thứ cần không?** “ReAct đúng, có trang. Attention thì chỉ đúng buổi, không ôn được. RAG sau khi mình chọn Day 3 thì đúng ý mình — phần chatbot có retrieval.”

**Mong hệ thống hoạt động thế nào?** “Nếu bài chưa có slide thì nói thẳng và đưa 1–2 hướng còn hỏi được. Đừng để mình ngồi chờ. Còn 3 nút RAG thì giữ — đừng tự chọn dùm, mình từng học RAG ở hơn một buổi.”

---

## 6. Phân tầng bằng chứng

| Tầng | Bằng chứng | Dùng để quyết định? |
|---|---|---|
| 1 Hành vi | ReAct: hỏi → bấm nguồn → đọc slide. Attention: hỏi lại, soi dropdown, **không khép job**. RAG: chọn Day 3, bấm nguồn | Có |
| 2 Nói lúc dùng | “Biết là bài 1 rồi mà đứng.” / “Bắt mình chọn buổi chứ không bịa.” | Có |
| 3 Giải thích khi hỏi | Muốn empty-state có bước tiếp; giữ G10 | Có |
| 4 Dự đoán | Không thu thập câu “sẽ dùng” | — |

Phiên **đạt** vì có failure thật (Day 1) và chỗ khó (G10), không phải toàn khen.

## 7. Mức nghiêm trọng

| ID | Phát hiện | Mức |
|---|---|---|
| V2-S2 | Day 1 route đúng nhưng hết đường ôn (không PDF, không bước tiếp) | S2 — trùng 3 case golden C01/C03/C09 |
| V2-S3 | G10: do dự ~12s trước khi chọn, nhưng tự xong | S3 — đúng hành vi thiết kế, không sửa thành auto-pick |
