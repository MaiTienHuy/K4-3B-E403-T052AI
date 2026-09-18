# Reflection cá nhân — Trịnh Xuân Huy

## 1. Vai trò cá nhân

Phụ trách **Prompt Engineering & AI Router** trong nhóm. Phần việc tập trung vào lớp logic quyết định: xác định câu hỏi của học viên thuộc bài đang mở, bài giảng khác, câu hỏi mơ hồ hay ngoài phạm vi; sau đó chọn cách xử lý phù hợp và an toàn.

## 2. Phần việc trực tiếp phụ trách

- Thiết kế và tinh chỉnh prompt định tuyến ý định cho Course Navigator.
- Xây dựng logic Cross-lecture Router để nhận diện buổi học đích khi học viên hỏi lại kiến thức cũ.
- Phân loại các nhóm câu hỏi chính: câu hỏi trong bài hiện tại, câu hỏi xuyên bài, câu hỏi mơ hồ, câu hỏi ngoài phạm vi, câu hỏi về slide cụ thể và câu hỏi cần ôn kiến thức nền.
- Thiết kế cơ chế G10: khi một khái niệm xuất hiện ở nhiều buổi hoặc câu hỏi chưa đủ rõ, hệ thống không tự đoán mà đưa ra các lựa chọn để người dùng xác nhận.
- Áp dụng G11 để giải thích vì sao hệ thống chọn một buổi học và cung cấp citation để người dùng kiểm chứng.
- Áp dụng G8/G9 để người dùng có thể bỏ qua gợi ý, đổi buổi học hoặc sửa quyết định định tuyến của hệ thống.
- Kiểm soát các trường hợp không được phép trả lời như giải hộ quiz, prompt injection và câu hỏi ngoài giáo trình.
- Phối hợp kiểm tra citation, bảo đảm hệ thống không tự tạo nguồn khi không tìm thấy căn cứ.

Các file cần hiểu và phối hợp kiểm tra gồm `codebase/decision.py`, `codebase/rag_store.py`, `codebase/concept_map.json` và kết quả trong `eval/`.

## 3. Cách ứng dụng AI trong quá trình xây dựng

Quy trình áp dụng:

1. Đọc yêu cầu trong `spec.md` và xác định rõ các nhánh hành vi cần có trước khi viết prompt.
2. Dùng AI để gợi ý các nhóm intent, edge case và cách diễn đạt câu hỏi tự nhiên của học viên.
3. Đối chiếu từng gợi ý với concept map, slide và Golden Set; loại bỏ những gợi ý không có căn cứ.
4. Thiết kế prompt có boundary rõ ràng: khi nào trả lời, khi nào hỏi lại, khi nào từ chối và khi nào phải kèm citation.
5. Chạy các câu hỏi trong Golden Set, đọc output thật và kiểm tra các điều kiện: route đúng, mode đúng, citation có thật và không bịa nguồn.
6. Sửa prompt hoặc logic tiền xử lý khi phát hiện hệ thống đoán bừa, route sai hoặc trả lời thiếu nguồn.

Điểm quan trọng rút ra là không thể chỉ yêu cầu AI “hãy trả lời chính xác”. Prompt phải mô tả được hành vi mong muốn, ngưỡng không chắc chắn, cách fallback và điều kiện để một câu trả lời được xem là đạt.

## 4. Bài học thực tế từ thất bại của nhóm

Các case C01, C03 và C09 cho thấy hệ thống nhận diện đúng câu hỏi hướng tới Day 1, nhưng kho chưa có `day1.pdf`, nên không lấy được trang nguồn và người học không thể tiếp tục ôn bài. Điều này cho thấy **route đúng chưa đồng nghĩa với hoàn thành job của người dùng**.

Bài học rút ra là Router phải kiểm tra cả khả năng phục vụ thực tế của nguồn đích. Nếu buổi được route tới chưa có file hoặc không có trang hợp lệ, hệ thống phải nói rõ trạng thái thiếu dữ liệu, đưa ra bước tiếp theo hoặc chuyển sang fallback; không nên tạo cảm giác nhiệm vụ đã hoàn tất chỉ vì tên buổi học được nhận diện đúng.

Một bài học khác là câu hỏi mơ hồ như “RAG là gì?” không nên được xử lý bằng cách chọn buổi có điểm truy xuất cao nhất. G10 có giá trị vì giữ quyền quyết định cho học viên khi cùng một khái niệm có nhiều cách hiểu. Trong giáo dục, hỏi lại đúng lúc an toàn hơn trả lời nhanh nhưng sai ngữ cảnh.

## 5. Hướng cải thiện

- Bổ sung kiểm tra khả dụng của file và trang nguồn trước khi xác nhận route thành công.
- Tách rõ ba trạng thái: route đúng, có nguồn hợp lệ và job đã khép.
- Mở rộng test cho các câu hỏi tiếng lóng, câu hỏi thiếu ngữ cảnh và các lượt hỏi tiếp sau khi route sai.
- Không chỉ đo Routing Accuracy; cần theo dõi thêm tỷ lệ người dùng mở được đúng nguồn và hoàn thành tác vụ.
- Khi trình bày với giám khảo, cần nói rõ giới hạn hiện tại: Day 1 đã được nhận diện trong logic nhưng PDF tương ứng chưa được nạp đầy đủ.

## 6. Kết luận

Phần việc của Trịnh Xuân Huy không chỉ là viết prompt để AI trả lời hay hơn. Trọng tâm là thiết kế một lớp quyết định có thể giải thích, có giới hạn rõ ràng và biết dừng khi thiếu căn cứ. Một hệ thống AI đáng tin cậy phải được đánh giá bằng toàn bộ hành trình của người dùng, từ nhận diện intent, chọn nguồn, hiển thị citation cho tới khả năng thực sự hoàn thành việc học.
