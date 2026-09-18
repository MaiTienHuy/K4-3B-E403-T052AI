# Phiên 01 — Nguyễn Thái Lương

| Trường | Giá trị |
|---|---|
| Thời điểm | 18/09/2026 · 19:10–19:22 |
| Vai | Học viên K4 · thường ôn bài cũ trước giờ học |
| Willing user CP1? | Có |
| Ngoài nhóm? | Có — không thuộc 4 thành viên Nhóm 03 |
| Facilitator | Mai Tiến Huy |
| Prototype | `BE+FE/app.py` · mặc định Day 5 |
| Task | Đang học bài 5, tìm và ôn lại **few-shot / prompting** đã học ở buổi trước |
| Cứu hộ đã dùng | “Cứ nói to suy nghĩ nhé.” (phút 2) · “Bạn sẽ làm gì tiếp?” (phút 4) |
| Thuyết minh màn hình? | Không |

---

## 1. Câu chuyện thật — trước khi mở prototype

**Câu hỏi:** Kể một tình huống thật từng gặp liên quan đến vấn đề sản phẩm giải quyết, trước khi được xem prototype.

**Trả lời nguyên văn:**

> Tuần rồi mình đang đọc slide Day 5 phần ngưỡng tự động thì muốn xem lại few-shot để nhớ mình từng viết ví dụ thế nào. Mình hỏi tutor VLearn luôn trong buổi đang mở. Nó bảo nội dung không có trong bài này, bảo mình tự quay về danh sách chọn bài. Mình thoát ra, mở Day 2 rồi Day 4, lật slide gần 5 phút mới thấy trang few-shot. Lúc quay lại Day 5 thì mất mạch, không nhớ mình đang đọc dở chỗ handoff.

**Hành vi / ngữ cảnh (tầng 1, kể lại trước khi thấy UI):** đã từng thoát buổi đang học, tự tìm 2 buổi, mất ~5 phút, đứt mạch.

---

## 2. Task đã giao (outcome)

> Bạn đang học bài 5 nhưng muốn ôn lại kiến thức về few-shot / prompting đã học ở những buổi trước. Hãy sử dụng hệ thống để tìm và ôn lại nội dung đó.

Không hướng dẫn nút, không giải thích UI.

---

## 3. Quan sát ~5 phút (tầng 1 — mạnh nhất)

| Phút | Hành vi quan sát được |
|---|---|
| 0:20 | Không đụng sidebar API. Nhìn cột trái (Day 5 đang mở), rồi nhìn ô chat. |
| 0:40 | Gõ: `ôn lại few-shot đã học ở buổi trước` · Enter. **Không** đổi bài thủ công trước khi hỏi. |
| 1:10 | Đọc câu trả lời có badge “Định tuyến liên bài” → Day 4. Gật đầu. |
| 1:25 | **Không bấm** nút nguồn. Kéo dropdown “Chọn bài giảng đang học”, mở Day 2, lật 3–4 trang. |
| 3:00 | Vẫn ở Day 2, chưa thấy few-shot. Cứu hộ: “Bạn sẽ làm gì tiếp?” |
| 3:15 | Quay lại khung chat, **bấm** `📄 Day 4: Prompt Engineering & Tool Calling (Trang …)`. Cột trái nhảy Day 4 đúng trang. |
| 3:25 | Đọc slide, gật, nói: “Đây, cái mình cần.” |
| 4:10 | Hỏi thêm `chỉ số tự động hóa` khi đang ở Day 4 → hệ thống trỏ Day 5 + nguồn. Lần này **bấm nguồn ngay** (hành vi sửa sau 1 lần kẹt). |
| 5:00 | Không khen suông. Tự dừng. |

**Kết luận tầng 1:** Job chỉ khép khi bấm nguồn. Trước đó người thử tự lội danh sách bài — đúng pain cũ, dù câu trả lời đã đúng buổi.

---

## 4. Nói lúc dùng (tầng 2)

- “Mình đang tự tìm few-shot trong danh sách bài… không biết cái nút xanh là nhảy trang.”
- “Đây, cái mình cần.” (sau khi bấm nguồn)
- “Lần này mình bấm luôn, khỏi chọn bài.” (lượt 2)

---

## 5. Năm câu — trả lời sau khi dùng / trong phiên

### Câu A — Tình huống thật (trước prototype)

Xem mục 1. Đồng ý đây đúng là việc mình hay gặp: đang học bài mới, cần ôn X ở bài cũ, tutor khóa context.

### Câu B — Nhận task theo mục tiêu

Đã nhận và tự làm task “đang học bài 5, ôn few-shot buổi trước” — không được chỉ nút.

### Câu C — Tự dùng ~5 phút, không hướng dẫn UI

Đã tự dùng. Lượt 1 kẹt vì không bấm nguồn. Lượt 2 tự bấm nguồn.

### Câu D — Nói suy nghĩ lúc dùng

Đã nói to: đang tìm few-shot, tưởng phải tự chọn bài bên trái, không hiểu nút nguồn.

### Câu E — Sau khi dùng

**Chỗ kẹt:** “Câu trả lời hiện rồi mà mình không biết phải bấm vào nguồn. Mình rẽ sang cái dropdown bài giảng như thói quen VLearn.”

**Kết quả có đúng thứ cần không?** “Đúng — few-shot ở Day 4, trang nó mở ra khớp cái mình nhớ. Lúc chưa bấm nút thì mình chưa ôn được, chỉ đọc chữ.”

**Mong hệ thống hoạt động thế nào?** “Chữ to hơn là ‘đã tìm thấy ở Day 4 trang này, bấm để mở’. Đừng bắt mình đoán nút. Nhưng đừng tự chuyển trang dùm — hôm nọ mình chỉ muốn đọc nhanh rồi quay lại Day 5.”

Không được hỏi “có thích không?”. Không ghi NPS.

---

## 6. Phân tầng bằng chứng

| Tầng | Bằng chứng | Dùng để quyết định? |
|---|---|---|
| 1 Hành vi | Tự hỏi trong Day 5; **không** đổi bài trước; sau câu trả lời thì **tự lội dropdown**; chỉ khép job khi bấm nguồn; lượt 2 bấm nguồn ngay | Có — chủ đề lặp |
| 2 Nói lúc dùng | “Không biết cái nút xanh là nhảy trang.” | Có |
| 3 Giải thích khi hỏi | “Đừng tự chuyển trang dùm… mình chỉ muốn đọc nhanh rồi quay lại.” | Có — lý do giữ G8 |
| 4 Dự đoán tương lai | (Không đẩy câu “sẽ dùng”) | Không dùng làm bằng chứng chính |

Phiên **đạt** vì không toàn lời khen: có kẹt thật, có hành động sửa, có lý do giữ nguyên việc không auto-redirect.

## 7. Mức nghiêm trọng

| ID | Phát hiện | Mức |
|---|---|---|
| V1-S2 | Không nhận ra nút nguồn = chưa khép job | S2 — lặp, chặn outcome |
| V1-S3 | Sidebar API nằm trên cùng, nhìn thoáng rồi bỏ | S3 — không chặn task |
