import os
import sys
import json
import chromadb
from chromadb.utils import embedding_functions

def load_day_to_chroma(day_num, collection):
    """Đọc file JSON của một ngày cụ thể và nạp vào ChromaDB"""
    json_path = f"day{day_num}_rag.json"
    if not os.path.exists(json_path):
        print(f"⚠️ Cảnh báo: Không tìm thấy file '{json_path}', bỏ qua.")
        return 0
        
    print(f"\n📄 Đang đọc dữ liệu từ {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        rag_data = json.load(f)
        
    documents = []
    metadatas = []
    ids = []
    
    for item in rag_data:
        documents.append(item["content"])
        metadatas.append({
            "source": item["source"],
            "page_index": item["page_index"]
        })
        # Tạo ID duy nhất cho mỗi slide, ví dụ: day4_page_1
        ids.append(f"day{day_num}_page_{item['page_index']}")
        
    if documents:
        print(f"Đang thêm {len(documents)} slide (Day {day_num}) vào ChromaDB...")
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Đã nạp thành công Day {day_num} ({len(documents)} slide)!")
        return len(documents)
    return 0

def main():
    # 1. Khởi tạo ChromaDB (lưu trữ tại thư mục ./chroma_db)
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # 2. Tạo collection để lưu dữ liệu (nếu đã có thì lấy lại)
    collection = client.get_or_create_collection(name="pdf_slides")
    
    # 3. Xác định các ngày cần nạp (mặc định Day 4, 5, 6 theo yêu cầu)
    if len(sys.argv) > 1:
        selected_days = []
        for arg in sys.argv[1:]:
            clean_arg = arg.lower().replace("day", "").strip()
            if clean_arg.isdigit():
                selected_days.append(int(clean_arg))
    else:
        selected_days = [4, 5, 6]

    print(f"🚀 Bắt đầu nạp dữ liệu vào ChromaDB cho các ngày: {selected_days}")
    total_added = 0
    for day in selected_days:
        total_added += load_day_to_chroma(day, collection)
        
    print(f"\n🎉 Hoàn tất! Tổng số slide vừa nạp/cập nhật: {total_added}")
    print(f"📊 Tổng số document hiện có trong collection 'pdf_slides': {collection.count()}")
    
    # 4. Test thử Query kiểm tra dữ liệu Day 4, 5, 6
    test_queries = [
        "Prompt Engineering là gì?",
        "Quản trị sản phẩm AI đối mặt với sự không chắc chắn thế nào?",
        "AI Project Management và vòng đời dự án"
    ]
    
    print("\n--- THỬ NGHIỆM TRUY VẤN KIỂM TRA ---")
    for q in test_queries:
        print(f"\n🔍 Query: '{q}'")
        results = collection.query(
            query_texts=[q],
            n_results=1
        )
        if results['documents'] and results['documents'][0]:
            meta = results['metadatas'][0][0]
            doc_snippet = results['documents'][0][0].replace('\n', ' ')[:120]
            print(f"👉 Nguồn: {meta['source']} (Trang {meta['page_index']})")
            print(f"   Trích đoạn: {doc_snippet}...")

if __name__ == "__main__":
    main()

