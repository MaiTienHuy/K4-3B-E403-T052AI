# Báo cáo đo lường chất lượng Lượt 1 (CP3)
- **Thời điểm chạy:** 2026-09-18 00:05:42
- **Engine thực thi:** `heuristic_baseline`
- **Tổng số test cases:** 20
- **Số case Pass:** 16
- **Tỷ lệ chính xác:** **80.0%**
- **Quality bar cam kết:** $\ge 85\%$

## Bảng chi tiết kết quả từng test case

| ID | Câu hỏi test | Lớp/Nhóm | Kỳ vọng | Thực tế | Hành vi | Trạng thái | Ghi chú / Nguyên nhân |
|---|---|---|---|---|---|:---:|---|
| GS-01 | tôi muốn học lại bài 1 | chatlog_real | `Day01` (route_and_summarize) | `Day01` (route_and_summarize) | route_and_summarize | ✅ PASS | Khớp từ khoá 'bài 1' của Day01 (AI & LLM Foundation) |
| GS-02 | giúp tôi ôn lại bài 1 | chatlog_real | `Day01` (route_and_summarize) | `Day01` (route_and_summarize) | route_and_summarize | ✅ PASS | Khớp từ khoá 'bài 1' của Day01 (AI & LLM Foundation) |
| GS-03 | bạn giúp tôi ôn lại bài 1 | chatlog_real | `Day01` (route_and_summarize) | `Day01` (route_and_summarize) | route_and_summarize | ✅ PASS | Khớp từ khoá 'bài 1' của Day01 (AI & LLM Foundation) |
| GS-04 | tóm tắt cho tôi buổi học hôm trước | chatlog_real | `Day04` (route_and_summarize) | `Day04` (route_and_summarize) | route_and_summarize | ✅ PASS | Ngữ cảnh hiện tại Day05 -> buổi trước là Day04 |
| GS-05 | mình muốn ôn tập lại buổi 1 | chatlog_real | `Day01` (route_and_summarize) | `Day01` (route_and_summarize) | route_and_summarize | ✅ PASS | Khớp từ khoá 'buổi 1' của Day01 (AI & LLM Foundation) |
| GS-06 | kiến thức này hôm trước thầy có nói ở buổi 3 đúng không, tóm tắt lại giúp mình | chatlog_real | `Day03` (route_and_summarize) | `Day05` (route_and_summarize) | route_and_summarize | ❌ FAIL | Lệch: Ngữ cảnh hiện tại Day06 -> buổi trước là Day05 |
| GS-07 | buổi 2 mình học về gì nhỉ | chatlog_real | `Day02` (route_and_summarize) | `Day02` (route_and_summarize) | route_and_summarize | ✅ PASS | Khớp từ khoá 'buổi 2' của Day02 (Xác định bài toán & JTBD) |
| GS-08 | cho mình hỏi lại phần Data Pipeline của Day 10 | chatlog_real | `Day10` (route_and_summarize) | `Day01` (route_and_summarize) | route_and_summarize | ❌ FAIL | Lệch: Khớp từ khoá 'day 1' của Day01 (AI & LLM Foundation) |
| GS-09 | bài hôm qua nói về AI Foundation là slide số mấy? | chatlog_real | `Day01` (route_and_summarize) | `Day02` (route_and_summarize) | route_and_summarize | ❌ FAIL | Lệch: Ngữ cảnh hiện tại Day03 -> buổi trước là Day02 |
| GS-10 | tóm tắt nhanh Day 05 phần Evaluation giúp mình | chatlog_real | `Day05` (route_and_summarize) | `Day05` (route_and_summarize) | route_and_summarize | ✅ PASS | Khớp từ khoá 'eval' của Day05 (Đánh giá & Kiểm thử AI (Eval cơ bản)) |
| GS-11 | tóm tắt cho mình bài học số 25 | hard_layer_1_grounding | `None` (refuse_out_of_curriculum) | `None` (refuse_out_of_curriculum) | refuse_out_of_curriculum | ✅ PASS | Khoá học chỉ có 20 buổi, không có bài 25 |
| GS-12 | giải thích thuyết tương đối hẹp của Einstein | hard_layer_1_grounding | `None` (refuse_out_of_curriculum) | `None` (refuse_out_of_curriculum) | refuse_out_of_curriculum | ✅ PASS | Nội dung hoàn toàn ngoài lề chương trình AI20k |
| GS-13 | buổi trước học gì | hard_layer_2_ambiguity | `None` (ask_clarification) | `None` (ask_clarification) | ask_clarification | ✅ PASS | Đang ở Day 01 nên không có buổi học trước đó |
| GS-14 | bài về Eval đo lường học ở đâu | hard_layer_2_ambiguity | `Day05` (ask_clarification) | `Day05` (ask_clarification) | ask_clarification | ✅ PASS | Khái niệm Eval có ở Day 05 (cơ bản) và Day 19 (nâng cao) |
| GS-15 | cho tôi xem trước đề thi tốt nghiệp của Day 20 | hard_layer_3_out_of_scope | `None` (refuse_out_of_scope) | `None` (refuse_out_of_scope) | refuse_out_of_scope | ✅ PASS | Yêu cầu tài liệu thi cử bảo mật ngoài thẩm quyền |
| GS-16 | đổi lịch học sang tối mai giúp tôi | hard_layer_3_out_of_scope | `None` (refuse_out_of_scope) | `None` (refuse_out_of_scope) | refuse_out_of_scope | ✅ PASS | Yêu cầu can thiệp hệ thống vận hành |
| GS-17 | bài Docker của thầy Nam dạy ở ngày mấy | hard_layer_4_domain | `Day04` (route_and_summarize) | `Day04` (route_and_summarize) | route_and_summarize | ✅ PASS | Docker được giảng dạy trong phần công cụ phát triển của Day 04 |
| GS-18 | giải hộ tôi bài tập nộp điểm của bài 3 | hard_layer_4_domain | `Day03` (refuse_homework_solving) | `Day03` (refuse_homework_solving) | refuse_homework_solving | ✅ PASS | Từ chối giải hộ bài tập để đảm bảo liêm chính học thuật |
| GS-19 | on lai bai 1 giup minh | rare_case | `Day01` (route_and_summarize) | `Day01` (route_and_summarize) | route_and_summarize | ✅ PASS | Khớp từ khoá 'bài 1' của Day01 (AI & LLM Foundation) |
| GS-20 | so sánh kiến thức Day 01 với Day 02 khác nhau chỗ nào | rare_case | `Day01` (route_and_summarize) | `None` (ask_clarification) | ask_clarification | ❌ FAIL | Lệch: Chưa xác định chắc chắn bài học tương ứng |

## Phân tích nguyên nhân các case Fail (nếu có)
- **GS-06** (`kiến thức này hôm trước thầy có nói ở buổi 3 đúng không, tóm tắt lại giúp mình`): Kỳ vọng `Day03` (route_and_summarize) nhưng nhận `Day05` (route_and_summarize). Nguyên nhân: Ngữ cảnh hiện tại Day06 -> buổi trước là Day05
- **GS-08** (`cho mình hỏi lại phần Data Pipeline của Day 10`): Kỳ vọng `Day10` (route_and_summarize) nhưng nhận `Day01` (route_and_summarize). Nguyên nhân: Khớp từ khoá 'day 1' của Day01 (AI & LLM Foundation)
- **GS-09** (`bài hôm qua nói về AI Foundation là slide số mấy?`): Kỳ vọng `Day01` (route_and_summarize) nhưng nhận `Day02` (route_and_summarize). Nguyên nhân: Ngữ cảnh hiện tại Day03 -> buổi trước là Day02
- **GS-20** (`so sánh kiến thức Day 01 với Day 02 khác nhau chỗ nào`): Kỳ vọng `Day01` (route_and_summarize) nhưng nhận `None` (ask_clarification). Nguyên nhân: Chưa xác định chắc chắn bài học tương ứng