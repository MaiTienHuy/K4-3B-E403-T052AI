# Bảng log validation R6

Nguồn: `session-01-nguyen-thai-luong.md`, `session-02-tran-cao-quoc-dinh.md`.  
Cách đọc: ưu tiên cột **Quan sát** (tầng 1) hơn quote (tầng 2–3). Không dùng câu “sẽ dùng” làm bằng chứng chính.

| Người thử (tên / vai — willing user?) | Task đã giao | Quan sát (hành vi) | Quote nguyên văn | Mức |
|---|---|---|---|---|
| Nguyễn Thái Lương · học viên K4, ôn bài cũ trước giờ học · **willing user CP1, ngoài nhóm** | Đang học bài 5, tìm và ôn lại few-shot / prompting buổi trước | 0:40 gõ câu hỏi trong Day 5, **không** đổi bài trước. 1:25 có câu trả lời Day 4 nhưng **không bấm nguồn** — mở dropdown, lật Day 2. 3:15 mới bấm nguồn, cột trái nhảy đúng trang, nói “Đây, cái mình cần.” Lượt 2 (`chỉ số tự động hóa`) bấm nguồn ngay. | “À mình đang tự tìm few-shot trong danh sách bài… không biết cái nút xanh là nhảy trang.” · “Đừng tự chuyển trang dùm — hôm nọ mình chỉ muốn đọc nhanh rồi quay lại Day 5.” | **S2** không nhận ra nút nguồn (chặn khép job). **S3** sidebar API không dùng. |
| Trần Cao Quốc Định · học viên K4, kẹt khi nối lý thuyết giữa buổi · **willing user CP1, ngoài nhóm** | Đang học bài 5, ôn ReAct; follow-up khó: attention rồi RAG | ReAct: hỏi → bấm nguồn Day 3 → đọc slide (khép). Attention: hệ thống nói Day 1, **không có trang**; soi dropdown không thấy Day 1; hỏi lại vẫn đứng. RAG: hệ thống đưa 3 lựa chọn, do dự ~12s, tự bấm Day 3, bấm nguồn. | “Nó biết là bài 1 rồi mà đứng. Ít ra cho mình hỏi cái khác còn slide, hoặc nói rõ bài 1 chưa nạp.” · “À, nó bắt mình chọn buổi chứ không bịa.” | **S2** Day 1 hết đường ôn. **S3** G10 do dự nhưng tự xong — giữ nguyên. |

## Chủ đề lặp (2/2 phiên)

1. Job chỉ xong khi **bấm nguồn ra đúng trang** — đọc chữ trong chat chưa đủ.
2. Day 1 / attention: route đúng nhưng **không ôn được** vì kho chưa có slide.

Không có phiên nào chỉ toàn lời khen.

## Quyết định trước demo

| Làm ngay | Giữ | Backlog |
|---|---|---|
| CTA “Đã tìm thấy ở Day X, trang Y — bấm nguồn để mở”; empty-state Day 1 có bước tiếp; mặc định mở Day 5; prompt theo outcome | Không tự nhảy trang (G8). Không tự chọn buổi khi G10. | Nạp `day1.pdf`. Ẩn API khỏi màn học viên. Đo recovery multi-turn. |
