# Phiên 03 — Nguyễn Xuân Trường

| Trường | Giá trị |
|---|---|
| Thời điểm | 18/09/2026 · 20:00–20:12 |
| Vai | Học viên K4 · cần tra cứu nhanh khái niệm kèm trích dẫn gốc |
| Willing user CP1? | Có |
| Ngoài nhóm? | Có — không thuộc 4 thành viên Nhóm 03 |
| Facilitator | Mai Tiến Huy |
| Prototype | `BE+FE/app.py` · mặc định Day 5 |
| Task | Đang học bài 5, tìm và ôn lại **tool calling / Chain-of-Thought** đã học ở buổi trước |
| Cứu hộ đã dùng | “Bạn sẽ làm gì tiếp?” (khi đã nhảy trang, tìm cách về Day 5) |
| Thuyết minh màn hình? | Không |

---

## 1. Câu chuyện thật — trước khi mở prototype

**Câu hỏi:** Kể một tình huống thật từng gặp liên quan đến vấn đề sản phẩm giải quyết, trước khi được xem prototype.

**Trả lời nguyên văn:**

> Nhóm mình chia phần lab, mình phải dẫn đúng slide tool calling để người kia đối chiếu. Mình đang mở Day 5 nên hỏi tutor “tool calling trang nào”. Nó bảo không có trong bài này, bảo tự chuyển. Mình mở Day 4, chụp đại vài slide, gửi nhóm. Sáng hôm sau bạn kia nói sai trang — mình gửi nhầm phần prompting tổng quan. Nếu lúc hỏi có số trang gắn sẵn thì khỏi cãi.

**Hành vi / ngữ cảnh (tầng 1, kể lại trước khi thấy UI):** đã từng thoát buổi đang học, tự đoán trang, gửi nhầm nguồn cho nhóm.

---

## 2. Task đã giao (outcome)

> Bạn đang học bài 5 nhưng muốn ôn lại kiến thức về tool calling / Chain-of-Thought đã học ở những buổi trước. Hãy sử dụng hệ thống để tìm và ôn lại nội dung đó.

Không hướng dẫn nút, không giải thích UI.

---

## 3. Quan sát ~5 phút (tầng 1 — mạnh nhất)

| Phút | Hành vi quan sát được |
|---|---|
| 0:25 | Nhìn ô chat trước, không đụng dropdown. Gõ: `ôn lại tool calling đã học ở buổi trước`. |
| 1:00 | Đọc badge định tuyến → Day 4. Mắt dừng ở dòng nguồn. **Bấm nguồn ngay** (không lội danh sách như Lương). |
| 1:10 | Cột trái nhảy Day 4. Đọc slide, gật. Nói: “Đây, có số trang.” Job ôn **khép**. |
| 2:00 | Hỏi thêm `Chain-of-Thought là gì` khi đang ở Day 4 → vẫn ra nguồn Day 4. Bấm nguồn. |
| 2:40 | Muốn quay lại mạch Day 5. Kéo dropdown chọn Day 5 — **về trang 1**, không về trang đang đọc dở. |
| 3:10 | Soi trên cùng cột trái, **không bấm** Hoàn tác (không để ý). Chọn lại Day 5, tự lật trang. |
| 4:20 | Hỏi `chỉ số tự động hóa sản phẩm AI` từ Day 5 vừa mở lại → ra nguồn Day 5. Bấm nguồn. |
| 5:10 | Tự dừng. Không khen suông. |

**Kết luận tầng 1:** Người cần citation thì bấm nguồn được. Job chưa trọn vì **quay lại buổi đang học** phải tự chọn dropdown và mất đúng trang cũ.

---

## 4. Nói lúc dùng (tầng 2)

---

## 5. Năm câu — trả lời sau khi dùng / trong phiên

### Câu A — Tình huống thật (trước prototype)

Xem mục 1. Đồng ý đúng việc mình hay gặp: đang học buổi mới, cần **đúng trang** bài cũ để gửi nhóm, tutor khóa context nên phải đoán trang.

### Câu B — Nhận task theo mục tiêu

Đã nhận và tự làm task “đang học bài 5, ôn tool calling / CoT buổi trước” — không được chỉ nút.

### Câu C — Tự dùng ~5 phút, không hướng dẫn UI

Đã tự dùng. Lượt hỏi ra nguồn và bấm được. Lượt về Day 5 bị đưa về trang 1.

### Câu D — Nói suy nghĩ lúc dùng

Đã nói to: cần số trang; sau khi nhảy thì đang tìm cách về đúng chỗ Day 5 vừa đọc.

### Câu E — Sau khi dùng

**Chỗ kẹt:** “Tìm bài cũ thì ổn. Về bài đang học mới khó — mình chọn lại Day 5 là nó về trang đầu, phải lật lại.”

**Kết quả có đúng thứ cần không?** “Đúng nội dung tool calling, có trang. Cái mình cần là cái đó. Chỉ tiếc lúc quay lại Day 5 không giữ trang cũ.”

**Mong hệ thống hoạt động thế nào?** “Giữ nút nguồn. Thêm cách về đúng trang đang học, đừng reset về trang 1. Đừng tự nhảy trang dùm lúc mới trả lời — mình muốn đọc chữ rồi tự bấm.”

Không được hỏi “có thích không?”. Không ghi NPS.

---

## 6. Phân tầng bằng chứng

| Tầng | Bằng chứng | Dùng để quyết định? |
|---|---|---|
| 1 Hành vi | Hỏi trong Day 5; **bấm nguồn ngay**; job ôn khép; về Day 5 bằng dropdown → **mất trang đang đọc** | Có |
| 2 Nói lúc dùng | “Đây, có số trang.” | Có |
| 3 Giải thích khi hỏi | Muốn về đúng trang đang học; không muốn auto-redirect lúc trả lời | Có — giữ G8, backlog hoàn tác/giữ trang |
| 4 Dự đoán tương lai | (Không đẩy câu “sẽ dùng”) | Không dùng làm bằng chứng chính |

Phiên **đạt** vì không toàn lời khen: citation ổn, chỗ kẹt thật ở bước quay lại buổi đang học.

## 7. Mức nghiêm trọng

| ID | Phát hiện | Mức |
|---|---|---|
| V3-S2 | Chọn lại bài trong dropdown đưa về trang 1, mất chỗ đang đọc | S2 — khép ôn rồi nhưng đứt mạch buổi hiện tại |
| V3-S3 | Không để ý nút Hoàn tác sau khi nhảy | S3 — có sẵn G8 nhưng không thấy |
