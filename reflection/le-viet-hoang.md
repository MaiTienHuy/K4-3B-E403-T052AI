# Reflection cá nhân — Lê Việt Hoàng

## 1. Vai trò cá nhân

Phụ trách **Code & Interactive Demo**, tập trung biến logic định tuyến và yêu cầu trong spec thành một prototype có thể thao tác được, đồng thời chuẩn bị luồng demo và phối hợp validation với willing users.

## 2. Phần việc trực tiếp phụ trách

- Phát triển giao diện prototype Streamlit trong `codebase/app.py`.
- Kết nối giao diện với lớp quyết định, kho truy xuất và dữ liệu slide.
- Hiển thị câu trả lời, citation, thẻ điều hướng và lựa chọn G10 cho người dùng.
- Xử lý thao tác chuyển buổi, ghi nhớ trang, hoàn tác và giữ nguyên context khi người dùng chỉ muốn đọc nhanh.
- Mô phỏng các luồng happy path, low-confidence, fallback và correction để nhóm quay demo.
- Phối hợp với willing users trong validation, ghi nhận điểm kẹt khi họ dùng nút nguồn, dropdown và hoàn tác.

## 3. Cách ứng dụng AI

AI được dùng để hỗ trợ viết khung giao diện, rà soát lỗi luồng thao tác và gợi ý cách tổ chức trạng thái trong Streamlit. Mỗi thay đổi do AI gợi ý đều được đối chiếu với spec và chạy thử bằng các case trong Golden Set trước khi giữ lại.

AI cũng được dùng để tạo các kịch bản kiểm tra nhanh cho việc chuyển bài, quay lại trang cũ, xử lý câu hỏi mơ hồ và hiển thị trạng thái không có nguồn. Phần giao diện cuối cùng phải ưu tiên quyền kiểm soát của người dùng, nên không áp dụng máy móc các đề xuất tự động redirect.

## 4. Bài học từ thất bại của nhóm

Validation với Nguyễn Thái Lương cho thấy câu trả lời có thể đúng nhưng job chưa khép nếu người dùng không nhận ra nút nguồn. Nguyễn Xuân Trường lại gặp vấn đề khi quay về Day 5 bị reset về trang 1 và không thấy nút hoàn tác. Những phản hồi này cho thấy tính năng đúng về mặt logic vẫn có thể khó dùng trong giao diện.

Case C01, C03 và C09 cũng cho thấy giao diện phải có empty-state rõ ràng khi route đúng Day 1 nhưng chưa có `day1.pdf`. Không nên để người dùng thấy hệ thống nhận diện đúng mà không biết phải làm gì tiếp theo.

## 5. Kết luận

Prototype không chỉ cần chạy được mà phải giúp người dùng hiểu bước tiếp theo. Citation, CTA, trạng thái thiếu dữ liệu và hoàn tác đều là một phần của sản phẩm, không phải chi tiết trang trí sau cùng.
