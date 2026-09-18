import os
import re
import fitz  # PyMuPDF
import streamlit as st
import chromadb
from dotenv import load_dotenv

from decision import decide
from rag_store import lecture_file, lecture_name, normalize_lecture

# Tải biến môi trường nếu có (override=True để tự nhận key mới khi sửa .env)
load_dotenv(override=True)

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="VinUni AI Study Assistant | NotebookLM Style",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS giao diện phong cách NotebookLM
st.markdown("""
<style>
    /* Tổng quan giao diện */
    .main {
        background-color: #fcfcfc;
    }
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .citation-btn {
        display: inline-block;
        background-color: #e8f0fe;
        color: #1967d2;
        border-radius: 16px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid #c2e7ff;
    }
    .stButton>button {
        border-radius: 8px;
    }
    .header-box {
        padding: 10px 16px;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .slide-badge {
        background-color: #f1f5f9;
        border-left: 4px solid #3b82f6;
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-weight: 600;
    }
    .undo-banner {
        background: #fff7ed;
        border: 1px solid #fdba74;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 10px;
        font-size: 0.92rem;
    }
    .g10-box {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 10px 12px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "vinuni_lectures"

# Danh mục bài giảng
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

def resolve_lecture(f_name_raw):
    lid = normalize_lecture(f_name_raw)
    if lid:
        return {
            "name": lecture_name(lid),
            "file": lecture_file(lid),
            "path": f"./slide/{lecture_file(lid)}",
        }
    return DEFAULT_LECTURES[0]


def _init_extra_state():
    defaults = {
        "nav_stack": [],
        "undo_banner": None,
        "dismiss_nav": [],
        "forced_lecture": None,
        "replay_question": None,
        "last_user_question": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_navigation(target_file, target_page):
    pdf_path = os.path.join("slide", str(target_file))
    if not os.path.exists(pdf_path):
        st.warning(f"Không mở được {target_file} — file PDF chưa có trong thư mục slide.")
        return
    st.session_state.nav_stack.append({
        "file": st.session_state.current_doc_file,
        "page": st.session_state.current_page,
    })
    st.session_state.undo_banner = {
        "from_file": st.session_state.current_doc_file,
        "from_page": st.session_state.current_page,
        "to_file": target_file,
        "to_page": int(target_page),
    }
    st.session_state.current_doc_file = target_file
    st.session_state.current_page = int(target_page)
    st.session_state.doc_version += 1


def undo_navigation():
    if not st.session_state.nav_stack:
        st.session_state.undo_banner = None
        return
    prev = st.session_state.nav_stack.pop()
    st.session_state.current_doc_file = prev["file"]
    st.session_state.current_page = prev["page"]
    st.session_state.undo_banner = None
    st.session_state.doc_version += 1


def reset_conversation(welcome: str):
    st.session_state.messages = [{"role": "assistant", "content": welcome, "citations": []}]
    st.session_state.forced_lecture = None
    st.session_state.replay_question = None
    st.session_state.last_user_question = None
    st.session_state.dismiss_nav = []
    st.session_state.undo_banner = None


def make_generate_fn(provider_name, key, model_name):
    def generate(system, user):
        if provider_name == "Google Gemini (Trực tiếp)":
            from google import genai
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=model_name,
                contents=f"{system}\n\n{user}",
            )
            return response.text
        import openai
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "VLearn Study Assistant",
            },
        )
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return completion.choices[0].message.content
    return generate


def run_turn(question, provider_name, key, model_name, forced=None):
    current_lid = normalize_lecture(st.session_state.current_doc_file) or "D3"
    generate_fn = make_generate_fn(provider_name, key, model_name) if key else None
    return decide(
        question,
        current_lecture=current_lid,
        current_page=st.session_state.current_page,
        forced_lecture=forced,
        generate_fn=generate_fn,
        citation_style="objects",
    )

@st.cache_resource
def get_chroma_collection(force_refresh=False):
    """Khởi tạo kết nối ChromaDB và lấy collection mới nhất"""
    if force_refresh:
        st.cache_resource.clear()
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name=COLLECTION_NAME)

collection = get_chroma_collection()

# Khởi tạo Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Xin chào! Tôi là trợ lý học tập AI được nâng cấp cho hệ thống VinUni. Khác với VLearn chỉ cho phép hỏi đáp trong từng bài riêng lẻ, tôi có thể **tra cứu và liên kết kiến thức xuyên suốt tất cả các bài giảng** (Day 2 đến Day 6).\n\nBạn có thể hỏi bất kỳ điều gì, và tôi sẽ gắn kèm liên kết trang slide cụ thể để bạn kiểm chứng!",
            "citations": []
        }
    ]

if "current_doc_file" not in st.session_state:
    st.session_state.current_doc_file = DEFAULT_LECTURES[1]["file"]  # Mặc định mở Day 3

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

if "doc_version" not in st.session_state:
    st.session_state.doc_version = 0

_init_extra_state()


# ==========================================
# SIDEBAR: Cấu hình & Quản lý bài giảng
# ==========================================
with st.sidebar:
    st.markdown("### 🎓 VinUni AI Assistant")
    st.caption("NotebookLM-style Cross-Lecture Q&A")
    st.divider()

    # 1. Chọn Nhà Cung Cấp (Provider)
    st.subheader("⚙️ Nhà Cung Cấp AI")
    provider = st.selectbox(
        "Nền tảng AI:",
        options=["Google Gemini (Trực tiếp)", "OpenRouter (Đa mô hình: DeepSeek, Llama, Claude...)"],
        index=0
    )

    if provider == "Google Gemini (Trực tiếp)":
        st.subheader("🔑 Google Gemini API Key")
        env_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        
        key_mode = st.radio(
            "Nguồn API Key:",
            options=["Dùng Key mặc định từ .env", "Tự nhập Key khác (Khi hết token / Dự phòng)"],
            index=0,
            key="gemini_key_mode",
            help="Khi key trong .env bị hết lượt gọi, hãy chuyển sang tuỳ chọn thứ 2 để dán key dự phòng"
        )

        if key_mode == "Dùng Key mặc định từ .env":
            if env_api_key:
                masked = env_api_key[:6] + "..." + env_api_key[-4:] if len(env_api_key) > 10 else "***"
                st.success(f"✅ Đang dùng key .env: `{masked}`")
                api_key = env_api_key
            else:
                st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY trong .env. Hãy điền vào file hoặc chọn 'Tự nhập Key khác' bên dưới.")
                api_key = ""
        else:
            api_key = st.text_input(
                "Nhập API Key Gemini dự phòng:",
                type="password",
                placeholder="Dán mã API Key mới tại đây...",
                help="Key này sẽ được ưu tiên sử dụng thay cho file .env"
            )
            if api_key:
                st.success("✅ Đang sử dụng key nhập thủ công!")

        # Chọn Model Gemini
        selected_model = st.selectbox(
            "🤖 Mô hình Gemini:",
            options=["gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"],
            index=0,
            help="gemini-3.7-flash và gemini-3.5-flash hiện đang chạy rất mượt và ổn định"
        )

    else:
        st.subheader("🔑 OpenRouter API Key")
        env_or_key = os.environ.get("OPENROUTER_API_KEY", "").strip()

        or_key_mode = st.radio(
            "Nguồn API Key OpenRouter:",
            options=["Dùng Key mặc định từ .env", "Tự nhập Key OpenRouter"],
            index=0 if env_or_key else 1,
            key="or_key_mode"
        )

        if or_key_mode == "Dùng Key mặc định từ .env" and env_or_key:
            masked = env_or_key[:8] + "..." + env_or_key[-4:] if len(env_or_key) > 12 else "***"
            st.success(f"✅ Đang dùng key .env: `{masked}`")
            api_key = env_or_key
        else:
            api_key = st.text_input(
                "Nhập OpenRouter API Key:",
                type="password",
                placeholder="sk-or-v1-...",
                help="Lấy API Key tại openrouter.ai/keys"
            )
            if api_key:
                st.success("✅ Đã nhận OpenRouter Key!")

        # Chọn Model OpenRouter
        or_model_choice = st.selectbox(
            "🤖 Mô hình OpenRouter:",
            options=[
                "deepseek/deepseek-chat",
                "deepseek/deepseek-r1",
                "meta-llama/llama-3.3-70b-instruct",
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o-mini",
                "google/gemini-2.0-flash-001",
                "qwen/qwen-2.5-72b-instruct",
                "Tự nhập Model ID khác..."
            ],
            index=0,
            help="Danh sách các mô hình hàng đầu thế giới qua OpenRouter"
        )

        if or_model_choice == "Tự nhập Model ID khác...":
            selected_model = st.text_input(
                "Nhập Model ID OpenRouter (VD: meta-llama/llama-3.1-8b-instruct:free):",
                value="meta-llama/llama-3.1-8b-instruct:free"
            )
        else:
            selected_model = or_model_choice

    st.divider()
    st.subheader("📚 Kho Bài Giảng Đã Nạp")
    try:
        coll = get_chroma_collection()
        total_items = coll.count()
        st.success(f"⚡ Đã kết nối ChromaDB: **{total_items} slides**")
    except Exception as e:
        st.warning(f"Chưa tải được dữ liệu: {e}")

    for lec in DEFAULT_LECTURES:
        exists = os.path.exists(lec["path"])
        icon = "🟢" if exists else "🔴"
        st.markdown(f"{icon} **{lec['name']}**  \n`{lec['file']}`")

    st.divider()
    st.info("💡 **Mẹo:** Bạn có thể bấm vào các nút trích dẫn trong câu trả lời của AI để khung xem slide bên trái tự động chuyển bài và nhảy trang.")
    
    if st.button("🗑️ Xoá toàn bộ lịch sử chat", use_container_width=True):
        reset_conversation("👋 Đã xoá toàn bộ lịch sử chat. Tôi có thể hỗ trợ gì cho bạn về các bài giảng từ Day 2 đến Day 6?")
        st.rerun()

# ==========================================
# BỐ CỤC CHÍNH: 2 CỘT (SLIDE VIEWER + CHAT)
# ==========================================
col_slide, col_chat = st.columns([5, 5], gap="large")

# ------------------------------------------
# CỘT TRÁI: Trình Xem Slide PDF (Slide Viewer)
# ------------------------------------------
with col_slide:
    st.markdown("### 📖 Trình Xem Bài Giảng (Slide Viewer)")
    if st.session_state.undo_banner:
        banner = st.session_state.undo_banner
        from_lid = normalize_lecture(banner["from_file"]) or "?"
        to_lid = normalize_lecture(banner["to_file"]) or "?"
        undo_c1, undo_c2 = st.columns([3.2, 1.8])
        with undo_c1:
            st.markdown(
                f"<div class='undo-banner'>Đã chuyển sang {to_lid} trang {banner['to_page']} "
                f"(trước đó {from_lid} trang {banner['from_page']}).</div>",
                unsafe_allow_html=True,
            )
        with undo_c2:
            if st.button("↩ Hoàn tác", use_container_width=True, key="undo_nav_btn"):
                undo_navigation()
                st.rerun()
    
    # Bộ chọn bài giảng đang xem
    doc_options = {d["file"]: d["name"] for d in DEFAULT_LECTURES}
    doc_keys = list(doc_options.keys())
    
    if "current_doc_file" not in st.session_state or st.session_state.current_doc_file not in doc_keys:
        st.session_state.current_doc_file = doc_keys[0]

    selected_file = st.selectbox(
        "Chọn bài giảng đang học:",
        options=doc_keys,
        format_func=lambda x: doc_options[x],
        index=doc_keys.index(st.session_state.current_doc_file),
        key=f"doc_select_widget_{st.session_state.doc_version}"
    )

    if selected_file != st.session_state.current_doc_file:
        st.session_state.current_doc_file = selected_file
        st.session_state.current_page = 1
        st.rerun()

    # Load file PDF động ngay theo bài giảng đang chọn
    current_doc_info = next((d for d in DEFAULT_LECTURES if d["file"] == st.session_state.current_doc_file), DEFAULT_LECTURES[0])
    pdf_path = current_doc_info["path"]
    if os.path.exists(pdf_path):
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        # Đảm bảo current_page hợp lệ
        if st.session_state.current_page > total_pages:
            st.session_state.current_page = total_pages
        if st.session_state.current_page < 1:
            st.session_state.current_page = 1

        # Thanh điều hướng trang
        nav_c1, nav_c2, nav_c3, nav_c4 = st.columns([1.5, 2, 2, 1.5])
        with nav_c1:
            if st.button("◀ Trang trước", disabled=(st.session_state.current_page <= 1), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
        with nav_c2:
            st.markdown(f"<div style='text-align: center; padding-top: 6px; font-weight: bold;'>Trang {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
        with nav_c3:
            jump_page = st.number_input(
                "Nhảy tới:",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.current_page,
                key=f"jump_{st.session_state.current_doc_file}_{st.session_state.doc_version}_{st.session_state.current_page}",
                label_visibility="collapsed"
            )
            if jump_page != st.session_state.current_page:
                st.session_state.current_page = jump_page
                st.rerun()
        with nav_c4:
            if st.button("Trang sau ▶", disabled=(st.session_state.current_page >= total_pages), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()

        # Render trang slide thành ảnh chất lượng cao
        page = doc[st.session_state.current_page - 1]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, use_container_width=True)
    else:
        st.error(f"Không tìm thấy file PDF tại: {pdf_path}")

# ------------------------------------------
# CỘT PHẢI: Khung Chat AI NotebookLM (RAG)
# ------------------------------------------
with col_chat:
    chat_hdr_col1, chat_hdr_col2 = st.columns([3.2, 1.8])
    with chat_hdr_col1:
        st.markdown("### 💬 Trợ Lý Đối Thoại Đa Bài Giảng")
        st.caption("Khắc phục hạn chế của VLearn — Hỏi đáp liên bài giảng")
    with chat_hdr_col2:
        if st.button("➕ Phiên mới", help="Tạo phiên hỏi đáp mới & làm sạch cuộc trò chuyện", use_container_width=True):
            reset_conversation(
                "✨ **Đã tạo phiên học mới!**\n\n"
                "Bạn muốn tìm hiểu hoặc so sánh kiến thức nào từ các bài giảng (Day 2 đến Day 6)? "
                "Hãy nhập câu hỏi bên dưới nhé!"
            )
            st.rerun()

    st.markdown("**Gợi ý — 4 đường đi khi tín hiệu rõ / mơ hồ:**")
    prompt_c1, prompt_c2 = st.columns(2)
    with prompt_c1:
        if st.button("📍 Chỉ số tự động hóa (route D5)", use_container_width=True):
            st.session_state.suggested_prompt = "chỉ số tự động hóa sản phẩm AI"
        if st.button("📄 Explain this slide", use_container_width=True):
            st.session_state.suggested_prompt = "explain this slide"
    with prompt_c2:
        if st.button("❓ Bữa trước cái chi dợ (G10)", use_container_width=True):
            st.session_state.suggested_prompt = "bữa trước cái chi dợ"
        if st.button("❓ RAG là gì (G10 hỏi lại)", use_container_width=True):
            st.session_state.suggested_prompt = "RAG là gì"

    st.divider()

    # Container hiển thị lịch sử chat
    chat_container = st.container(height=480)
    last_idx = len(st.session_state.messages) - 1
    with chat_container:
        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("mode"):
                    conf = msg.get("confidence")
                    conf_txt = f" · conf {conf}" if conf is not None else ""
                    st.caption(f"Nhánh `{msg.get('mode')}`{conf_txt}")

                if msg.get("mode") == "g10" and msg.get("candidates") and idx == last_idx:
                    st.markdown('<div class="g10-box"><b>Thu hẹp phạm vi (G10)</b> — chọn một buổi để mình trả lời đúng ngữ cảnh.</div>', unsafe_allow_html=True)
                    opt_cols = st.columns(min(len(msg["candidates"]), 3))
                    labels = msg.get("candidate_labels") or {}
                    for o_idx, lid in enumerate(msg["candidates"]):
                        with opt_cols[o_idx % 3]:
                            label = labels.get(lid) or lecture_name(lid)
                            if st.button(f"{lid}: {label}", key=f"g10_{idx}_{lid}", use_container_width=True):
                                st.session_state.forced_lecture = lid
                                st.session_state.replay_question = msg.get("source_question") or st.session_state.last_user_question
                                st.rerun()

                nav_on = (
                    msg.get("nav_suggestion")
                    and idx not in st.session_state.dismiss_nav
                    and msg.get("target_lecture")
                )
                if nav_on:
                    target_lid = msg["target_lecture"]
                    nav_c1, nav_c2, nav_c3 = st.columns([2.2, 1.4, 1.4])
                    with nav_c1:
                        st.caption(f"📍 Gợi ý chuyển sang {lecture_name(target_lid)}")
                    with nav_c2:
                        if msg.get("citations") and st.button("👉 Chuyển sang bài này", key=f"nav_go_{idx}", use_container_width=True):
                            cit0 = msg["citations"][0]
                            apply_navigation(cit0["file"], cit0["page"])
                            st.rerun()
                    with nav_c3:
                        if st.button("✕ Bỏ qua gợi ý", key=f"nav_dismiss_{idx}", use_container_width=True):
                            if idx not in st.session_state.dismiss_nav:
                                st.session_state.dismiss_nav.append(idx)
                            st.rerun()

                if nav_on and idx == last_idx:
                    visible = [d for d in DEFAULT_LECTURES if os.path.exists(d["path"])]
                    ids = [normalize_lecture(d["file"]) for d in visible]
                    current_target = msg.get("target_lecture")
                    pick = st.selectbox(
                        "✎ Đổi bài nếu định tuyến chưa đúng",
                        options=ids,
                        index=ids.index(current_target) if current_target in ids else 0,
                        format_func=lambda x: lecture_name(x),
                        key=f"g9_select_{idx}",
                    )
                    if st.button("Áp dụng buổi đã chọn", key=f"g9_apply_{idx}"):
                        st.session_state.forced_lecture = pick
                        st.session_state.replay_question = msg.get("source_question") or st.session_state.last_user_question
                        st.rerun()

                if msg.get("citations"):
                    st.markdown("**📌 Nguồn trích dẫn (Bấm để nhảy tới slide):**")
                    cols = st.columns(min(len(msg["citations"]), 3))
                    for c_idx, cit in enumerate(msg["citations"]):
                        col_target = cols[c_idx % 3]
                        with col_target:
                            btn_label = f"📄 {cit['doc_name']} (Trang {cit['page']})"
                            if st.button(btn_label, key=f"btn_cit_{idx}_{c_idx}", use_container_width=True):
                                apply_navigation(cit["file"], int(cit["page"]))
                                st.rerun()

    user_input = st.chat_input("Hỏi về bài đang mở, slide này, hoặc ôn buổi khác (Day 2–6)...")
    replay_forced = None
    if st.session_state.replay_question:
        user_input = st.session_state.pop("replay_question")
        replay_forced = st.session_state.pop("forced_lecture", None)
    elif "suggested_prompt" in st.session_state:
        user_input = st.session_state.pop("suggested_prompt")

    if user_input:
        display_q = user_input
        if replay_forced:
            display_q = f"Mình chọn {replay_forced}: {user_input}"
        st.session_state.messages.append({"role": "user", "content": display_q, "citations": []})
        st.session_state.last_user_question = user_input

        spinner_title = "Đang phân loại ý định, truy xuất đúng buổi và kiểm trích dẫn..."
        with st.spinner(spinner_title):
            try:
                decision = run_turn(
                    user_input,
                    provider,
                    api_key,
                    selected_model,
                    forced=replay_forced,
                )
                clean_answer = re.sub(
                    r"\[REF:([^:]+):(\d+)\]",
                    r"*(📄 \1 - Trang \2)*",
                    decision.get("answer") or "",
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": clean_answer,
                    "citations": decision.get("citation_objects") or decision.get("citations") or [],
                    "mode": decision.get("mode"),
                    "intent": decision.get("intent"),
                    "confidence": decision.get("confidence"),
                    "target_lecture": decision.get("target_lecture"),
                    "candidates": decision.get("candidates") or [],
                    "candidate_labels": decision.get("candidate_labels") or {},
                    "nav_suggestion": decision.get("nav_suggestion"),
                    "needs_user_choice": decision.get("needs_user_choice"),
                    "source_question": user_input,
                })
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str.lower():
                    tip = (
                        "⚠️ **LỖI MÁY CHỦ QUÁ TẢI TẠM THỜI (503 UNAVAILABLE):**\n\n"
                        "Mô hình này hiện đang có lượng truy cập đột biến.\n\n"
                        "👉 **Cách khắc phục ngay:** Bạn hãy chờ khoảng 3–5 giây rồi gửi lại câu hỏi, hoặc đổi sang mô hình khác ở thanh bên Sidebar!"
                    )
                elif "401" in err_str or "auth" in err_str.lower():
                    tip = (
                        "⚠️ **LỖI XÁC THỰC API KEY (401 Unauthorized):**\n\n"
                        "Mã API Key bạn nhập không hợp lệ hoặc đã hết hạn. Vui lòng kiểm tra lại API Key trong thanh bên Sidebar!"
                    )
                elif "402" in err_str or "credit" in err_str.lower():
                    tip = (
                        "⚠️ **LỖI HẾT SỐ DƯ (402 Payment Required):**\n\n"
                        "Tài khoản OpenRouter của bạn không đủ credits để gọi mô hình này. Hãy nạp thêm credits hoặc chọn các model miễn phí (`:free`) nhé!"
                    )
                elif "429" in err_str or "ResourceExhausted" in err_str or "quota" in err_str.lower():
                    tip = (
                        "⚠️ **LỖI HẾT LƯỢT GỌI / HẾT TOKEN (Quota Exceeded):**\n\n"
                        "API Key hiện tại của bạn đã dùng hết hạn mức của nhà cung cấp (mã lỗi 429). \n\n"
                        "👉 **Cách khắc phục ngay:** Bạn hãy nhìn sang thanh bên trái (Sidebar), chọn 'Tự nhập Key khác' để dán key dự phòng hoặc đổi sang nhà cung cấp/mô hình khác nhé!"
                    )
                else:
                    tip = f"❌ Đã xảy ra lỗi khi xử lý câu hỏi: `{err_str}`"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": tip,
                    "citations": [],
                })

        st.rerun()
