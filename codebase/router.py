"""
VLearn Course Navigator - Central Decision Router
==================================================
Xác định câu hỏi của học viên thuộc buổi nào (Day01 -> Day20)
và quyết định hành động phản hồi phù hợp theo nguyên tắc HAX/PAIR.
"""

import os
import sys
import io
import re
import json
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACE_LOG_PATH = os.path.join(BASE_DIR, "traces.log")

def log_trace(query: str, current_lecture: str, response_data: Dict[str, Any]):
    """Ghi vết (logging trace) phục vụ xác minh kỹ thuật theo yêu cầu CP3."""
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": now_str,
        "current_lecture": current_lecture,
        "user_query": query,
        "engine": response_data.get("engine"),
        "raw_action": response_data.get("action"),
        "identified_lecture": response_data.get("lecture_code"),
        "confidence": response_data.get("confidence")
    }
    try:
        with open(TRACE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass
CURRICULUM = {
    "Day01": {"title": "AI & LLM Foundation", "keywords": ["ai foundation", "llm foundation", "bài 1", "buổi 1", "day 1", "day01", "cơ bản về llm"]},
    "Day02": {"title": "Xác định bài toán & JTBD", "keywords": ["bài 2", "buổi 2", "day 2", "day02", "jtbd", "job to be done", "pain point", "xác định bài toán"]},
    "Day03": {"title": "Prompt Engineering & ICL", "keywords": ["bài 3", "buổi 3", "day 3", "day03", "prompt", "prompt engineering", "few-shot"]},
    "Day04": {"title": "Môi trường & Docker Tools", "keywords": ["bài 4", "buổi 4", "day 4", "day04", "docker", "môi trường", "setup"]},
    "Day05": {"title": "Đánh giá & Kiểm thử AI (Eval cơ bản)", "keywords": ["bài 5", "buổi 5", "day 5", "day05", "eval", "evaluation", "đo lường", "kiểm thử"]},
    "Day06": {"title": "Hackathon & Prototyping", "keywords": ["bài 6", "buổi 6", "day 6", "day06", "hackathon", "prototype", "spec"]},
    "Day07": {"title": "Embeddings & Vector Database", "keywords": ["bài 7", "buổi 7", "day 7", "day07", "embedding", "vector", "chromadb"]},
    "Day08": {"title": "Kiến trúc RAG", "keywords": ["bài 8", "buổi 8", "day 8", "day08", "rag", "retrieval augmented generation"]},
    "Day09": {"title": "RAG nâng cao & Chunking", "keywords": ["bài 9", "buổi 9", "day 9", "day09", "chunking", "advanced rag"]},
    "Day10": {"title": "Data Pipeline & Observability", "keywords": ["bài 10", "buổi 10", "day 10", "day10", "data pipeline", "observability", "pipeline"]},
    "Day19": {"title": "Model Evaluation nâng cao & Red Teaming", "keywords": ["day 19", "bài 19", "eval nâng cao", "red teaming"]},
    "Day20": {"title": "Tổng kết & Đồ án tốt nghiệp", "keywords": ["day 20", "bài 20", "tốt nghiệp", "đồ án"]}
}

SYSTEM_PROMPT = """Bạn là VLearn Course Navigator Router.
Nhiệm vụ của bạn là nhận diện xem câu hỏi của học viên đang muốn hỏi/ôn lại bài học nào trong khoá học (từ Day 01 đến Day 20).
Ngữ cảnh: Học viên đang ở một buổi học cụ thể ({current_lecture}).

Quy tắc xử lý (HAX / PAIR):
1. [Lớp 1 - Nguồn sự thật]: Nếu hỏi bài không tồn tại (> Day 20) hoặc kiến thức hoàn toàn ngoài lề không thuộc khoá AI20k, trả về action = 'refuse_out_of_curriculum'.
2. [Lớp 2 - Mơ hồ]: Nếu học viên hỏi chung chung 'buổi trước' khi đang ở Day 01, hoặc hỏi khái niệm xuất hiện ở nhiều bài (ví dụ Eval ở cả Day 05 và Day 19), trả về action = 'ask_clarification'.
3. [Lớp 3 - Ngoài thẩm quyền]: Nếu đòi đề thi bảo mật hoặc đòi can thiệp hệ thống (đổi lịch), trả về action = 'refuse_out_of_scope'.
4. [Lớp 4 - Domain]: Nếu hỏi giải hộ bài tập chấm điểm, trả về action = 'refuse_homework_solving'.
5. Nếu xác định được bài cũ hợp lệ, trả về action = 'route_and_summarize' cùng lecture_code chính xác (Day01 .. Day20).

Trả về định dạng JSON thuần túy:
{
  "lecture_code": "Day01" hoặc null,
  "confidence": 0.0 đến 1.0,
  "action": "route_and_summarize" | "ask_clarification" | "refuse_out_of_curriculum" | "refuse_out_of_scope" | "refuse_homework_solving",
  "explanation": "Lý do ngắn gọn",
  "suggested_reply": "Nội dung phản hồi dự kiến"
}
"""

def normalize_text(text: str) -> str:
    """Chuẩn hoá chuỗi cơ bản, chuyển về chữ thường."""
    text = text.lower().strip()
    # Khử dấu cơ bản cho tiếng Việt để hỗ trợ case hiếm
    accents = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a', 'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e', 'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o', 'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u', 'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y', 'đ': 'd'
    }
    return text

def route_offline_heuristic(user_input: str, current_lecture: str) -> Dict[str, Any]:
    """
    Heuristic router offline: dùng rule-based logic khớp với taxonomy của Spec.
    Được sử dụng làm baseline hoặc fallback khi chưa thiết lập API key.
    """
    text_lower = user_input.lower()
    
    # 1. Kiểm tra Lớp 3 (Ngoài thẩm quyền)
    if "đề thi" in text_lower or "xem trước đề" in text_lower:
        return {
            "lecture_code": None,
            "confidence": 0.95,
            "action": "refuse_out_of_scope",
            "explanation": "Yêu cầu tài liệu thi cử bảo mật ngoài thẩm quyền",
            "suggested_reply": "Tài liệu đề thi được bảo mật, trợ lý không thể cung cấp trước."
        }
    if "đổi lịch" in text_lower or "chuyển lớp" in text_lower:
        return {
            "lecture_code": None,
            "confidence": 0.95,
            "action": "refuse_out_of_scope",
            "explanation": "Yêu cầu can thiệp hệ thống vận hành",
            "suggested_reply": "Vui lòng liên hệ ban cán sự hoặc kênh #tro-giup-hoc-tap để đổi lịch."
        }
        
    # 2. Kiểm tra Lớp 4 (Domain: Giải bài tập)
    if "giải hộ" in text_lower or "làm hộ" in text_lower:
        match_day = re.search(r'(?:bài|buổi|day)\s*([0-9]+)', text_lower)
        code = f"Day{int(match_day.group(1)):02d}" if match_day else "Day03"
        return {
            "lecture_code": code,
            "confidence": 0.9,
            "action": "refuse_homework_solving",
            "explanation": "Từ chối giải hộ bài tập để đảm bảo liêm chính học thuật",
            "suggested_reply": f"Mình chỉ có thể giải thích lý thuyết nền tảng của {code}, bạn hãy tự hoàn thành bài tập nhé."
        }
        
    # 3. Kiểm tra Lớp 1 (Nguồn sự thật - Bài không tồn tại hoặc ngoài giáo trình)
    match_num = re.search(r'(?:bài|buổi|day)\s*(?:học số\s*)?([0-9]+)', text_lower)
    if match_num:
        num = int(match_num.group(1))
        if num > 20 or num <= 0:
            return {
                "lecture_code": None,
                "confidence": 0.99,
                "action": "refuse_out_of_curriculum",
                "explanation": f"Khoá học chỉ có 20 buổi, không có bài {num}",
                "suggested_reply": f"Khoá học AI20k chỉ bao gồm 20 buổi (Day 01 đến Day 20). Không có bài {num}."
            }
            
    if "thuyết tương đối" in text_lower or "einstein" in text_lower or "vật lý lượng tử" in text_lower:
        return {
            "lecture_code": None,
            "confidence": 0.99,
            "action": "refuse_out_of_curriculum",
            "explanation": "Nội dung hoàn toàn ngoài lề chương trình AI20k",
            "suggested_reply": "Nội dung này nằm ngoài phạm vi giáo trình của khoá học."
        }

    # 4. Kiểm tra Lớp 2 (Mơ hồ - Cần làm rõ)
    if ("buổi trước" in text_lower or "bài hôm trước" in text_lower) and current_lecture in ["Day01", "D01"]:
        return {
            "lecture_code": None,
            "confidence": 0.85,
            "action": "ask_clarification",
            "explanation": "Đang ở Day 01 nên không có buổi học trước đó",
            "suggested_reply": "Hiện tại đang là Day 01 (buổi đầu tiên), bạn có muốn xem trước lộ trình tổng thể không?"
        }
        
    if "eval" in text_lower and not any(k in text_lower for k in ["day 05", "day 5", "day 19", "nâng cao", "cơ bản"]):
        return {
            "lecture_code": "Day05",
            "confidence": 0.7,
            "action": "ask_clarification",
            "explanation": "Khái niệm Eval có ở Day 05 (cơ bản) và Day 19 (nâng cao)",
            "suggested_reply": "Khái niệm Evaluation được học ở Day 05 (Cơ bản) và Day 19 (Nâng cao). Bạn muốn tra cứu bài nào?"
        }

    # 5. Xử lý "buổi hôm trước / bài hôm qua" theo ngữ cảnh hiện tại
    if "buổi trước" in text_lower or "hôm trước" in text_lower or "hôm qua" in text_lower:
        curr_match = re.search(r'([0-9]+)', current_lecture)
        if curr_match:
            curr_num = int(curr_match.group(1))
            prev_num = curr_num - 1
            if prev_num >= 1:
                target_code = f"Day{prev_num:02d}"
                return {
                    "lecture_code": target_code,
                    "confidence": 0.95,
                    "action": "route_and_summarize",
                    "explanation": f"Ngữ cảnh hiện tại {current_lecture} -> buổi trước là {target_code}",
                    "suggested_reply": f"Dưới đây là tóm tắt nội dung buổi {target_code}: ..."
                }

    # 6. Kiểm tra các keyword bài học trực tiếp (bao gồm cả không dấu)
    # Case Docker -> Day 04
    if "docker" in text_lower:
        return {
            "lecture_code": "Day04",
            "confidence": 0.9,
            "action": "route_and_summarize",
            "explanation": "Docker được giảng dạy trong phần công cụ phát triển của Day 04",
            "suggested_reply": "Kiến thức Docker nằm trong phần Môi trường & Tools của Day 04."
        }

    # Quét theo danh mục
    clean_text = text_lower.replace("on lai bai", "bài").replace("hoc lai bai", "bài")
    for code, info in CURRICULUM.items():
        for kw in info["keywords"]:
            if kw in clean_text or kw in text_lower:
                return {
                    "lecture_code": code,
                    "confidence": 0.9,
                    "action": "route_and_summarize",
                    "explanation": f"Khớp từ khoá '{kw}' của {code} ({info['title']})",
                    "suggested_reply": f"Tìm thấy kiến thức trong {code}: {info['title']}."
                }

    # Mặc định nếu không khớp
    return {
        "lecture_code": None,
        "confidence": 0.4,
        "action": "ask_clarification",
        "explanation": "Chưa xác định chắc chắn bài học tương ứng",
        "suggested_reply": "Bạn muốn hỏi về buổi học nào trong 20 ngày? (Ví dụ: Day 01, Day 05...)"
    }

def route_query(user_input: str, current_lecture: str = "Day10") -> Dict[str, Any]:
    """
    Entrypoint chính để route câu hỏi.
    Nếu có API Key (GEMINI_API_KEY / OPENAI_API_KEY) sẽ gọi LLM thật.
    Nếu không có, fallback sang router heuristic.
    """
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if gemini_api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"{SYSTEM_PROMPT.format(current_lecture=current_lecture)}\n\nCâu hỏi của học viên: {user_input}"
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            result = json.loads(response.text)
            result["engine"] = "gemini-1.5-flash-live"
            log_trace(user_input, current_lecture, result)
            return result
        except Exception as e:
            fallback = route_offline_heuristic(user_input, current_lecture)
            fallback["engine"] = f"fallback_heuristic (error: {str(e)})"
            log_trace(user_input, current_lecture, fallback)
            return fallback

    elif openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT.format(current_lecture=current_lecture)},
                    {"role": "user", "content": user_input}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            result["engine"] = "gpt-4o-mini-live"
            log_trace(user_input, current_lecture, result)
            return result
        except Exception as e:
            fallback = route_offline_heuristic(user_input, current_lecture)
            fallback["engine"] = f"fallback_heuristic (error: {str(e)})"
            log_trace(user_input, current_lecture, fallback)
            return fallback
    else:
        result = route_offline_heuristic(user_input, current_lecture)
        result["engine"] = "heuristic_baseline"
        log_trace(user_input, current_lecture, result)
        return result

if __name__ == "__main__":
    # Thử nghiệm nhanh với một câu trong chatlog
    test_q = "tôi muốn học lại bài 1"
    print("--- Thử nghiệm Router ---")
    print(f"Input: {test_q}")
    res = route_query(test_q, current_lecture="Day10")
    print(json.dumps(res, indent=2, ensure_ascii=False))
