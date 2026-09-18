# Reflection cá nhân — Mai Tiến Huy

**Thành viên:** Mai Tiến Huy

## 1. Vai trò cá nhân

Phụ trách **Product & AI Spec** và điều phối chung dự án. Vai trò này là biến vấn đề học viên gặp phải thành một lát cắt sản phẩm rõ ràng, viết tiêu chí đánh giá và bảo đảm các phần spec, prototype, evaluation và validation cùng hướng về một mục tiêu.

## 2. Phần việc trực tiếp phụ trách

- Định hình bài toán Course Navigator và xác định người dùng, job executor, pain point và lát cắt một câu.
- Viết và hoàn thiện `spec.md` theo cấu trúc yêu cầu của hackathon.
- Chuẩn hóa mục tiêu sản phẩm, non-goals, các đường đi trải nghiệm và quality bar.
- Điều phối việc kết nối giữa logic router, giao diện prototype, bộ Golden Set và validation với willing users.
- Theo dõi các giới hạn còn tồn tại và cập nhật Changelog, đặc biệt vấn đề thiếu `day1.pdf`.
- Chuẩn bị nội dung để nhóm giải thích rõ vì sao chọn automation có điều kiện thay vì tự động chuyển bài hoàn toàn.

## 3. Cách ứng dụng AI

AI được dùng để brainstorm cách diễn đạt problem statement, JTBD, kịch bản lỗi và tiêu chí nghiệm thu. Các gợi ý sau đó được đối chiếu với dữ liệu chatlog, concept map, kết quả evaluation và phản hồi từ người dùng trước khi đưa vào spec.

AI cũng hỗ trợ rà soát phần còn thiếu trong tài liệu, gợi ý edge case và kiểm tra tính nhất quán giữa mục tiêu sản phẩm với hành vi prototype. Output của AI không được dùng làm bằng chứng trực tiếp; số liệu, quote và kết quả đo phải lấy từ file hoặc lần chạy thực tế trong repo.

## 4. Bài học từ thất bại của nhóm

Các case C01, C03 và C09 cho thấy hệ thống route đúng Day 1 nhưng chưa có `day1.pdf`, nên người dùng không mở được nguồn. Bài học rút ra là một spec tốt phải phân biệt rõ **đúng quyết định AI** với **hoàn thành job của người dùng**. Không thể chỉ báo routing accuracy cao rồi kết luận sản phẩm đã hoạt động tốt.

Từ đó, cần tự khai rõ giới hạn trong spec. Thiếu dữ liệu, thiếu trang nguồn hoặc chưa đo recovery multi-turn phải được ghi rõ thay vì che giấu. Điều này giúp nhóm trung thực khi trình bày và biết chính xác backlog cần xử lý tiếp.

## 5. Kết luận

Product & AI Spec không chỉ là viết tài liệu. Đó là việc biến một ý tưởng thành hệ thống quyết định có thể kiểm chứng: làm cho ai, giải quyết việc gì, thế nào là đạt, thất bại ở đâu và cần nói thật điều gì với người dùng.
