# Khảo sát chatlog thật — `tutor_turns.csv` (đã kiểm bằng số liệu)

## 1. Quy mô & cấu trúc
- Số lượt: **13.494** (= 13.494 `turn_id` duy nhất). *(Số dòng thô trên đĩa là 121.316 vì ô CSV có xuống dòng.)*
- Cột: `turn_id, period, cohort_hint, asked_at_vn, student, lecture_code, lecture_title, course_id, is_preset, q_len, student_question, tutor_reply, reply_len, move_used, understanding_level, has_citation, grade_missing, rating, reply_ms`
- **ĐA KHOÁ** (`course_id`): COMP2010 **6609** · BIOM3010 **2156** · K4P1 **2146** · COMP4010 **1225** · L2-L3-K4P1 **951** · COMP3011 **382** · VinUni-AIInAction-3 **17** · (trống) 8
- Cohort: K3 **10397** · K4 **3097**
- `is_preset`: False **10427** · True **3067** (True = prompt hệ thống, KHÔNG phải câu hỏi tự nhiên)

## 2. Kiểm chứng các mã lượt đang được trích trong hướng dẫn

| Mã | `student_question` (CSV) | lecture_code / course_id | Kết luận |
|---|---|---|---|
| T04265 | giúp tôi ôn lại bài 1 | D21 / COMP2010 | Tồn tại — nhưng lời đáp KHÁC quote trong spec (viết lại) |
| T04272 | bạn giúp tôi ôn lại bài 1 | D21 / COMP2010 | Tồn tại — quote spec không nguyên văn |
| T04261 | tôi muốn học lại bài 1 | D21 / COMP2010 | Tồn tại — quote spec không nguyên văn |
| T00540 | Tóm tắt nội dung slide đầu tiên của Day 1 giúp mình. | D11 / COMP2010 | Tồn tại, dùng được |
| T00175 | (Trang 9, đoạn được chọn: "bạn hiểu gì về slide 9") | D17 / COMP2010 | `is_preset=True` |
| T00061 | (Trang 17, đoạn được chọn: "giải thích kĩ slide 18") | D17 / COMP2010 | `is_preset=True` |
| T03378 | (Trang 14, đoạn được chọn: "explain this slide in 200 words") | D06 / COMP2010 | `is_preset=True` |
| T01484 | (Trang 12, đoạn được chọn: "tóm tắt cho tôi buổi học hôm trước") | D05 / COMP2010 | `is_preset=True` |
| T08912 | (Đang học phần "Day16-Track2-CloudInfrastructure"…) Giải thích rõ đoạn này… "Model security + data encryption…" | D01 / BIOM3010 | `is_preset=True` — **KHÔNG khớp mô tả trong spec** |

## 3. Kết luận
1. **Mã lượt trích tồn tại thật**, NHƯNG **lời đáp tutor trong spec §1 bị viết lại** → khi viết case phải **copy nguyên văn** `student_question` + `tutor_reply` từ CSV.
2. Bối cảnh khác giả định "AI Product K4 / Day 3" → các lượt nêu trên là **K3 / COMP2010 / D21** → phải ghi đúng `course_id` + `lecture_code`.
3. **T08912 trích sai** → bỏ hoặc thay bằng lượt khác.
4. Nhiều lượt là `is_preset=True` → **không nên** dùng làm "case chatlog thật".
5. Lượt tự nhiên (không preset) theo lớp: **cross_lec 39 · slideN 1371 · ambiguous 282 · outscope 97 · slang 2**.

## 4. File dùng ngay
- **`eval/chatlog_ung_vien.csv`** — các lượt ứng viên (12/lớp) đã gắn cột `bucket` (cross_lec / slideN / ambiguous / outscope / slang), đủ để chọn **≥10 case**.
- Nếu LLM có quyền đọc repo: trỏ thẳng tới `tutor_turns.csv` (13.494 lượt). Nếu chỉ được gửi file: gửi kèm `chatlog_ung_vien.csv` (nhỏ) thay cho file 22MB.
