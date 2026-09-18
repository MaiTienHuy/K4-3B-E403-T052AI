import json
import fitz  # PyMuPDF

def extract_slides_for_rag(pdf_path, output_json_path):
    """
    Trích xuất text từ file PDF (slide) để dùng cho RAG.
    Mỗi page sẽ được lưu thành một document/chunk với page_index.
    """
    print(f"Đang mở file: {pdf_path}")
    doc = fitz.open(pdf_path)
    rag_data = []

    for page_num, page in enumerate(doc):
        # Lấy số trang thực tế (bắt đầu từ 1)
        page_index = page_num + 1
        
        # Trích xuất text. 
        # Tùy chọn "text" trả về chuỗi text thuần túy. Có thể dùng "blocks" nếu muốn cấu trúc hơn.
        text = page.get_text("text")
        
        # Làm sạch text sơ bộ (xóa các khoảng trắng thừa, dòng trống vô nghĩa)
        cleaned_text = "\n".join([line.strip() for line in text.split('\n') if line.strip()])
        
        # Bỏ qua các slide trống
        if cleaned_text:
            rag_data.append({
                "page_index": page_index,
                "content": cleaned_text,
                "source": pdf_path
            })
            
    # Lưu ra file JSON để dễ dàng nạp vào Vector Database (Chroma, FAISS, Qdrant,...)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(rag_data, f, ensure_ascii=False, indent=2)
        
    print(f"Đã trích xuất xong {len(rag_data)} slide (bỏ qua các slide trống).")
    print(f"Dữ liệu được lưu tại: {output_json_path}")

if __name__ == "__main__":
    import os
    import sys

    # Danh sách các ngày cần trích xuất (mặc định là day 4, 5, 6 theo yêu cầu)
    # Có thể truyền qua tham số dòng lệnh, ví dụ: python extract_slides_for_rag.py 4 5 6
    if len(sys.argv) > 1:
        selected_days = []
        for arg in sys.argv[1:]:
            clean_arg = arg.lower().replace("day", "").strip()
            if clean_arg.isdigit():
                selected_days.append(int(clean_arg))
    else:
        selected_days = [4, 5, 6]

    base_dir = "./slide"
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"🚀 Bắt đầu trích xuất slide cho các ngày: {selected_days}")
    for day in selected_days:
        input_pdf = os.path.join(base_dir, f"day{day}.pdf")
        output_json = os.path.join(output_dir, f"day{day}_rag.json")
        
        print(f"\n--- Đang xử lý Day {day} ---")
        if not os.path.exists(input_pdf):
            print(f"⚠️ Cảnh báo: Không tìm thấy file '{input_pdf}', bỏ qua.")
            continue
            
        try:
            extract_slides_for_rag(input_pdf, output_json)
        except Exception as e:
            print(f"❌ Lỗi khi xử lý Day {day}: {e}")

    print("\n✨ Hoàn tất xử lý trích xuất slide!")

