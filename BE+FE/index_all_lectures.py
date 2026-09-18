import os
import fitz  # PyMuPDF
import chromadb

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "vinuni_lectures"

# Danh sách các bài giảng mặc định
DEFAULT_LECTURES = [
    {
        "name": "Day 2: AI Prompting & Tools",
        "file": "day2.pdf",
        "path": "./slide/day2.pdf"
    },
    {
        "name": "Day 3: ReAct Pattern & Agent Loop",
        "file": "day3.pdf",
        "path": "./slide/day3.pdf"
    },
    {
        "name": "Day 4: Prompt Engineering & Tool Calling",
        "file": "day4.pdf",
        "path": "./slide/day4.pdf"
    },
    {
        "name": "Day 5: Quản trị sản phẩm AI",
        "file": "day5.pdf",
        "path": "./slide/day5.pdf"
    },
    {
        "name": "Day 6: AI Product & Project Management",
        "file": "day6.pdf",
        "path": "./slide/day6.pdf"
    }
]


def get_chroma_collection():
    """Khởi tạo hoặc tải collection từ ChromaDB"""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return client, collection

def index_pdf_file(collection, doc_name: str, doc_file: str, pdf_path: str):
    """Trích xuất và đánh chỉ mục từng trang của 1 file PDF vào ChromaDB"""
    if not os.path.exists(pdf_path):
        print(f"⚠️ Cảnh báo: Không tìm thấy file '{pdf_path}', bỏ qua.")
        return 0

    print(f"📄 Đang xử lý: {doc_name} ({pdf_path})")
    doc = fitz.open(pdf_path)
    
    documents = []
    metadatas = []
    ids = []

    for page_num, page in enumerate(doc):
        page_index = page_num + 1
        text = page.get_text("text")
        cleaned_text = "\n".join([line.strip() for line in text.split('\n') if line.strip()])

        # Lưu cả trang trống để đảm bảo RAG vẫn nhận diện được slide nếu cần, 
        # nhưng ưu tiên slide có text
        content = cleaned_text if cleaned_text else f"[Slide hình ảnh / Slide tiêu đề trang {page_index}]"
        
        doc_id = f"{doc_file}_page_{page_index}"
        documents.append(content)
        metadatas.append({
            "doc_name": doc_name,
            "doc_file": doc_file,
            "doc_path": pdf_path,
            "page_index": page_index
        })
        ids.append(doc_id)

    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Đã nạp thành công {len(documents)} slide cho '{doc_name}'.")

    return len(documents)

def index_all_default_lectures():
    """Nạp tất cả các bài giảng mặc định vào ChromaDB"""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("🗑️ Đã xóa collection cũ để làm mới dữ liệu.")
    except Exception:
        pass
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    total_slides = 0
    print("🚀 Bắt đầu quá trình nạp đa bài giảng vào ChromaDB...")
    
    for lec in DEFAULT_LECTURES:
        slides_count = index_pdf_file(
            collection=collection,
            doc_name=lec["name"],
            doc_file=lec["file"],
            pdf_path=lec["path"]
        )
        total_slides += slides_count

    print(f"\n🎉 HOÀN TẤT: Tổng cộng {total_slides} slide từ các bài giảng đã sẵn sàng trong ChromaDB!")
    return total_slides

if __name__ == "__main__":
    index_all_default_lectures()
