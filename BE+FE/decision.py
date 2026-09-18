"""Lớp quyết định: tín hiệu → confidence → 4 đường đi. LLM chỉ sinh câu khi đã được phép."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from rag_store import (
    get_page,
    lecture_file,
    lecture_name,
    lecture_scores,
    load_concept_map,
    normalize_lecture,
    page_exists,
    previous_lecture,
    retrieve,
    retrieval_margin,
    topic_index,
    tokenize,
)

REF_RE = re.compile(r"\[REF:([^:]+):(\d+)\]")

CONTENT_VERBS = (
    "ôn", "on lai", "học lại", "hoc lai", "tóm tắt", "tom tat", "summarize",
    "giải thích", "giai thich", "explain", "review", "so sánh", "so sanh",
    "nhắc", "mô tả", "mo ta", "định nghĩa", "dinh nghia", "kể",
)

DEIXIS_RE = re.compile(
    r"\b(this slide|slide này|trang này|slide hiện tại|slide hien tai|"
    r"explain this|giải thích slide|giai thich slide)\b",
    re.I,
)
SLIDE_NUM_RE = re.compile(r"\b(?:slide|trang)\s*(\d+)\b", re.I)
LECTURE_RE = re.compile(
    r"\b(?:day|bài|bai|buổi|buoi)\s*([1-6])\b|\bday([1-6])\.pdf\b|\bd([1-6])\b",
    re.I,
)
RELATIVE_RE = re.compile(
    r"hôm trước|hom truoc|buổi trước|buoi truoc|bữa trước|bua truoc|"
    r"hôm qua|hom qua|bài trước|bai truoc|buổi liền trước",
    re.I,
)
PREREQ_RE = re.compile(
    r"nền gì|nen gi|tiên quyết|tien quyet|cần nhớ|can nho|để hiểu|de hieu|"
    r"prerequisite|nền tảng để",
    re.I,
)
QUIZ_RE = re.compile(r"giải hộ|giai ho|quiz|trắc nghiệm|trac nghiem|đáp án câu|dap an cau", re.I)
INJECTION_RE = re.compile(
    r"bỏ qua hướng dẫn|bo qua huong dan|ignore (previous|instructions)|"
    r"bạn là model|ban la model|you are now|jailbreak|đóng vai",
    re.I,
)
OOS_RE = re.compile(
    r"solidity|smart contract|marketing|flutter|erc-?20|ethereum|"
    r"bài thơ|bai tho|làm thơ|lam tho",
    re.I,
)
CORRECTION_RE = re.compile(
    r"không phải|khong phai|sai rồi|sai roi|đổi sang|doi sang|ý mình là|y minh la",
    re.I,
)
SLANG_ONLY_RE = re.compile(
    r"^(cái|chi|dợ|do|gì|gi|vậy|vay|nhỉ|the|à|ơi|mình|toi|tôi|bạn|ban|ạ|đi|xem|nào|nay|kia|phần|phan|dợ)+\s*$",
    re.I,
)

ANSWER_MODES = {"cross_lecture", "slide_locate", "prereq_bridge", "current"}


@dataclass
class Signals:
    lecture_ids: list[str] = field(default_factory=list)
    slide_num: int | None = None
    has_deixis: bool = False
    has_relative_time: bool = False
    has_content: bool = False
    is_quiz: bool = False
    is_injection: bool = False
    is_oos: bool = False
    is_prereq: bool = False
    is_correction: bool = False
    concept_ids: list[str] = field(default_factory=list)
    resolved_lecture: str | None = None
    collision: bool = False
    candidates: list[str] = field(default_factory=list)
    candidate_labels: dict[str, str] = field(default_factory=dict)
    expand_query: str = ""


def _norm(text: str) -> str:
    return " ".join(tokenize(text))


def _concept_match(question: str) -> Signals:
    cmap = load_concept_map()
    qn = _norm(question)
    sig = Signals()
    for concept in cmap["concepts"]:
        aliases = [_norm(a) for a in concept.get("aliases") or []]
        only = [_norm(a) for a in concept.get("ambiguous_if_only") or []]
        hit_alias = any(a and a in qn for a in aliases)
        hit_only = any(a and a in qn for a in only)
        if not hit_alias and not hit_only:
            continue
        sig.concept_ids.append(concept["id"])
        senses = concept.get("senses") or {}
        sense_hits = []
        for lid, words in senses.items():
            if any(_norm(w) and _norm(w) in qn for w in words):
                sense_hits.append(lid)
        primary = concept.get("primary")
        also = list(concept.get("also") or [])
        labels = concept.get("labels") or {}
        if hit_only and not hit_alias and not sense_hits:
            pool = ([primary] if primary else []) + also
            sig.collision = True
            sig.candidates = [x for x in pool if x]
            sig.candidate_labels.update({k: labels[k] for k in sig.candidates if k in labels})
            continue
        if primary and (not also or (sense_hits == [primary]) or (not sense_hits and hit_alias)):
            if sense_hits and primary not in sense_hits and len(sense_hits) == 1:
                sig.resolved_lecture = sense_hits[0]
            elif not sense_hits and also and not hit_alias:
                sig.collision = True
                sig.candidates = [primary, *also]
            else:
                sig.resolved_lecture = primary
                expand = (concept.get("expand_query") or {}).get(primary, "")
                if expand:
                    sig.expand_query = f"{question} {expand}"
        elif sense_hits == 1:
            sig.resolved_lecture = sense_hits[0]
        else:
            pool = []
            if primary:
                pool.append(primary)
            pool.extend(also)
            if len(set(pool)) > 1:
                sig.collision = True
                sig.candidates = list(dict.fromkeys(pool))
            elif pool:
                sig.resolved_lecture = pool[0]
        for lid, label in labels.items():
            sig.candidate_labels[lid] = label
        if sig.resolved_lecture:
            expand = (concept.get("expand_query") or {}).get(sig.resolved_lecture, "")
            if expand:
                sig.expand_query = f"{question} {expand}"
    if sig.collision and sig.resolved_lecture:
        # alias chung thắng nghĩa riêng thì vẫn collision
        if any(c.get("id") in sig.concept_ids and not c.get("primary") for c in cmap["concepts"]):
            sig.resolved_lecture = None
    return sig


def extract_signals(question: str) -> Signals:
    q = question or ""
    sig = _concept_match(q)
    for match in LECTURE_RE.finditer(q):
        num = match.group(1) or match.group(2) or match.group(3)
        if num:
            lid = f"D{num}"
            if lid not in sig.lecture_ids:
                sig.lecture_ids.append(lid)
    slide = SLIDE_NUM_RE.search(q)
    if slide:
        sig.slide_num = int(slide.group(1))
    sig.has_deixis = bool(DEIXIS_RE.search(q))
    sig.has_relative_time = bool(RELATIVE_RE.search(q))
    sig.is_quiz = bool(QUIZ_RE.search(q))
    sig.is_injection = bool(INJECTION_RE.search(q))
    sig.is_oos = bool(OOS_RE.search(q))
    sig.is_prereq = bool(PREREQ_RE.search(q))
    sig.is_correction = bool(CORRECTION_RE.search(q))
    qn = _norm(q)
    has_verb = any(v in qn for v in CONTENT_VERBS)
    leftover = RELATIVE_RE.sub(" ", q)
    leftover = LECTURE_RE.sub(" ", leftover)
    leftover = DEIXIS_RE.sub(" ", leftover)
    leftover_n = _norm(leftover)
    leftover_is_empty = (not leftover_n) or bool(SLANG_ONLY_RE.match(leftover_n))
    sig.has_content = bool(
        has_verb or sig.resolved_lecture or sig.collision or sig.concept_ids or (sig.slide_num and not leftover_is_empty)
    )
    if leftover_is_empty and not has_verb and not sig.resolved_lecture and not sig.collision:
        sig.has_content = False
    return sig


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _score(retrieval_top: float, margin: float, concept_hit: float, specificity: float,
           collision: bool, thin: bool) -> float:
    score = (
        0.35 * _clip(retrieval_top, 0, 1)
        + 0.25 * _clip(margin, 0, 1)
        + 0.20 * _clip(concept_hit, 0, 1)
        + 0.20 * _clip(specificity, 0, 1)
    )
    if collision:
        score -= 0.30
    if thin:
        score -= 0.40
    return _clip(score, 0.0, 1.0)


def _hits_to_citations(hits: list[dict], limit: int = 3) -> list[dict]:
    out = []
    seen = set()
    for hit in hits:
        key = (hit["file"], int(hit["page"]))
        if key in seen:
            continue
        if not page_exists(hit["file"], hit["page"]) and hit.get("source") != "viewport":
            # viewport / json đã là nguồn thật
            if not hit.get("text"):
                continue
        seen.add(key)
        out.append({
            "doc_name": hit.get("doc_name") or lecture_name(hit["lecture"]),
            "file": hit["file"],
            "page": int(hit["page"]),
        })
        if len(out) >= limit:
            break
    return out


def _format_eval_citations(citations: list[dict]) -> list[str]:
    return [f"[{c['file']}:{c['page']}]" for c in citations]


def _gate_refs(answer: str, allowed: set[tuple[str, int]]) -> tuple[str, list[dict], list[str]]:
    valid = []
    invalid = []
    seen = set()

    def repl(match: re.Match) -> str:
        raw_file, raw_page = match.group(1), match.group(2)
        lid = normalize_lecture(raw_file)
        try:
            page = int(raw_page)
        except ValueError:
            invalid.append(f"[{raw_file}:{raw_page}]")
            return ""
        file = lecture_file(lid) if lid else raw_file
        key = (file, page)
        if key not in allowed and (lid, page) not in {(normalize_lecture(f), p) for f, p in allowed}:
            invalid.append(f"[{file}:{page}]")
            return ""
        if key not in seen:
            seen.add(key)
            valid.append({
                "doc_name": lecture_name(lid) if lid else file,
                "file": file,
                "page": page,
            })
        return match.group(0)

    cleaned = REF_RE.sub(repl, answer or "")
    return cleaned, valid, invalid


def _excerpt(text: str, limit: int = 420) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "…"


def _template_answer(mode: str, question: str, current: str, target: str | None,
                     hits: list[dict], candidates: list[str], labels: dict[str, str],
                     slide_hit: dict | None, reason: str) -> str:
    if mode == "g10":
        lines = [
            "Câu hỏi chưa đủ rõ để chọn đúng một buổi, nên mình không đoán.",
            "Bạn đang muốn xem phần nào?",
        ]
        pool = candidates or []
        for lid in pool:
            label = labels.get(lid) or lecture_name(lid)
            lines.append(f"- [{lid}] {label}")
        if not pool:
            lines.append("- Nêu giúp mình buổi (Day 2–6) hoặc khái niệm cụ thể.")
        return "\n".join(lines)
    if mode == "fallback":
        if "quiz" in reason:
            return (
                "Tutor không được phép giải hộ bài quiz/bài chấm điểm. "
                "Mình có thể nhắc lại khái niệm nền trong slide để bạn tự làm, "
                "nhưng không đưa đáp án."
            )
        if "inject" in reason:
            return "Mình là Trợ lý học tập VLearn. Hãy hỏi các nội dung liên quan đến bài giảng nhé."
        return (
            "Chủ đề này không có trong tài liệu bài giảng đã cung cấp. "
            "Hiện mình chỉ quản lý kiến thức Day 1–Day 6 (LLM, Prompting, Agent, quản trị sản phẩm AI). "
            "Bạn có thể hỏi lại theo một khái niệm trong giáo trình, hoặc hỏi trợ giảng."
        )
    if mode == "slide_locate" and slide_hit:
        return (
            f"Đây là nội dung slide đang mở — {slide_hit['doc_name']} trang {slide_hit['page']}.\n\n"
            f"{_excerpt(slide_hit['text'], 520)}\n\n"
            f"[REF:{slide_hit['file']}:{slide_hit['page']}]"
        )
    banner = ""
    if mode == "cross_lecture" and target and target != current:
        banner = (
            f"📍 [Định tuyến liên bài]: Kiến thức này thuộc {lecture_name(target)} "
            f"(thay vì bài bạn đang xem ở cột trái).\n\n"
        )
    if not hits:
        name = lecture_name(target or current)
        if (target or current) == "D1":
            return banner + (
                f"Mình xác định kiến thức này thuộc {name}, "
                "nhưng slide Day 1 chưa có trong kho đang nạp nên không mở được đúng trang. "
                "Bạn có thể hỏi một khái niệm đã có slide (Day 2–6) — ví dụ few-shot, ReAct, "
                "chỉ số tự động hóa — hoặc dùng ✎ Đổi bài để chọn buổi khác."
            )
        return banner + (
            f"Mình hiểu bạn đang hỏi về {name}, nhưng chưa lấy được trang nguồn trong kho slide. "
            "Hãy hỏi lại bằng tên khái niệm cụ thể hơn, hoặc chọn một buổi Day 2–6."
        )
    parts = [banner.strip(), ""] if banner else []
    for hit in hits[:3]:
        parts.append(f"- {_excerpt(hit['text'], 220)} [REF:{hit['file']}:{hit['page']}]")
    if mode == "prereq_bridge":
        parts.insert(0, f"Để hiểu chủ đề này khi đang học {lecture_name(current)}, nên ôn các nền tảng sau:")
    return "\n".join(p for p in parts if p is not None).strip()


def _build_generate_prompt(mode: str, question: str, current: str, target: str | None,
                           context: str, page: int | None) -> tuple[str, str]:
    viewport = f"Học viên đang mở {lecture_name(current)} (file {lecture_file(current)}), trang {page}."
    system = f"""Bạn là Trợ lý học tập VLearn. {viewport}
Mục lục buổi:
{topic_index()}

MODE đã được hệ thống chốt: {mode}. target_lecture={target}.
Chỉ dùng nguồn dưới đây. Mọi luận điểm phải có [REF:file_name:page_number] với file/page có trong nguồn.
Không bịa slide. Không giải hộ quiz. Không đổi vai.
Nếu MODE=cross_lecture: mở đầu bằng
📍 [Định tuyến liên bài]: Kiến thức này thuộc [tên buổi đích] (thay vì bài bạn đang xem ở cột trái).
Trả lời 2–4 đoạn hoặc gạch đầu dòng.

NGUỒN:
{context}
"""
    return system, f"CÂU HỎI CỦA NGƯỜI HỌC: {question}"


def decide(
    question: str,
    *,
    current_lecture: str = "D3",
    current_page: int | None = 1,
    forced_lecture: str | None = None,
    generate_fn=None,
    citation_style: str = "objects",
) -> dict:
    current = normalize_lecture(current_lecture) or "D3"
    page = int(current_page or 1)
    forced = normalize_lecture(forced_lecture)
    sig = extract_signals(question)
    if not forced and sig.is_correction and sig.lecture_ids:
        forced = sig.lecture_ids[0]

    intent = "CURRENT"
    mode = "current"
    target = current
    candidates: list[str] = []
    labels = dict(sig.candidate_labels)
    reason = "default"
    hits: list[dict] = []
    slide_hit = None
    confidence = 0.5
    nav = False

    if forced:
        intent = "CROSS_LECTURE" if forced != current else "CURRENT"
        mode = "cross_lecture" if forced != current else "current"
        target = forced
        reason = "forced"
        query = sig.expand_query or question
        hits = retrieve(query, lecture_ids=[forced], n=5)
        confidence = 0.9
        nav = forced != current
    elif sig.is_quiz:
        intent, mode, target, reason = "OUT_OF_SCOPE", "fallback", None, "quiz"
        confidence = 0.2
    elif sig.is_injection:
        intent, mode, target, reason = "OUT_OF_SCOPE", "fallback", None, "inject"
        confidence = 0.15
    elif sig.is_oos:
        intent, mode, target, reason = "OUT_OF_SCOPE", "fallback", None, "oos"
        confidence = 0.2
    elif sig.slide_num is not None or sig.has_deixis:
        intent, mode, reason = "SLIDE_LOCATE", "slide_locate", "viewport"
        target = current
        want_page = sig.slide_num if sig.slide_num is not None else page
        slide_hit = get_page(current, want_page)
        if slide_hit is None:
            # trang không có text trong JSON — vẫn bám viewport để không hỏi lại
            slide_hit = {
                "lecture": current,
                "file": lecture_file(current),
                "doc_name": lecture_name(current),
                "page": want_page,
                "text": f"[Slide trang {want_page} của {lecture_name(current)}]",
                "source": "viewport",
            }
        neighbors = []
        for offset in (-1, 0, 1):
            nxt = get_page(current, want_page + offset)
            if nxt:
                neighbors.append({**nxt, "score": 1.0 if offset == 0 else 0.4, "source": "viewport"})
        hits = neighbors or [{**slide_hit, "score": 1.0, "source": "viewport"}]
        confidence = 0.92 if sig.slide_num or page else 0.7
        nav = False
    elif sig.collision and not sig.resolved_lecture:
        intent, mode, target, reason = "AMBIGUOUS", "g10", None, "concept_collision"
        candidates = sig.candidates or []
        confidence = 0.58
    elif sig.is_prereq:
        intent, mode, reason = "PREREQ_BRIDGE", "prereq_bridge", "prereq"
        target = current
        prev = previous_lecture(current)
        scope = [current] + ([prev] if prev else [])
        hits = retrieve(sig.expand_query or question, lecture_ids=scope, n=5)
        confidence = 0.88
        nav = False
    elif sig.resolved_lecture:
        target = sig.resolved_lecture
        intent = "CROSS_LECTURE" if target != current else "CURRENT"
        mode = "cross_lecture" if target != current else "current"
        reason = "concept_primary"
        hits = retrieve(sig.expand_query or question, lecture_ids=[target], n=5)
        scores = lecture_scores(hits)
        margin = retrieval_margin(scores)
        top = max(scores.values()) if scores else 0.6
        confidence = _score(top, margin, 1.0, 0.85, False, False)
        if confidence < 0.85:
            confidence = 0.88  # nghĩa đã chốt bằng bản đồ khái niệm
        nav = target != current
    elif sig.lecture_ids and sig.has_content:
        target = sig.lecture_ids[0]
        intent, mode, reason = "CROSS_LECTURE", "cross_lecture", "named_lecture"
        hits = retrieve(question, lecture_ids=[target], n=5)
        if not hits:
            home = get_page(target, 1)
            if home:
                hits = [{**home, "score": 0.5, "source": "toc"}]
        confidence = 0.9
        nav = target != current
    elif sig.has_relative_time and sig.has_content:
        prev = previous_lecture(current)
        if prev:
            target = prev
            intent, mode, reason = "CROSS_LECTURE", "cross_lecture", "previous"
            hits = retrieve(question, lecture_ids=[prev], n=5)
            if not hits:
                home = get_page(prev, 1) or get_page(prev, 2)
                if home:
                    hits = [{**home, "score": 0.5, "source": "toc"}]
            confidence = 0.9
            nav = True
        else:
            intent, mode, target, reason = "AMBIGUOUS", "g10", None, "no_previous"
            candidates = [current]
            confidence = 0.55
    elif sig.lecture_ids or sig.has_relative_time or not sig.has_content:
        intent, mode, target, reason = "AMBIGUOUS", "g10", None, "thin_question"
        if sig.lecture_ids:
            candidates = list(sig.lecture_ids)
            for lid in candidates:
                labels.setdefault(lid, lecture_name(lid))
        elif sig.has_relative_time:
            prev = previous_lecture(current)
            candidates = [c for c in (prev, current) if c]
            labels.update({lid: lecture_name(lid) for lid in candidates})
        else:
            candidates = [current]
            if previous_lecture(current):
                candidates.insert(0, previous_lecture(current))
            labels.update({lid: lecture_name(lid) for lid in candidates})
        confidence = 0.52
    else:
        hits = retrieve(question, n=6)
        scores = lecture_scores(hits)
        margin = retrieval_margin(scores)
        top_lid = max(scores, key=scores.get) if scores else None
        top = scores.get(top_lid, 0.0) if top_lid else 0.0
        confidence = _score(top, margin, 0.0, 0.3, len(scores) > 1 and margin < 0.08, False)
        if not hits or confidence < 0.50:
            intent, mode, target, reason = "OUT_OF_SCOPE", "fallback", None, "low_retrieval"
            hits = []
        elif 0.50 <= confidence < 0.85 or (len(scores) > 1 and margin < 0.08):
            intent, mode, target, reason = "AMBIGUOUS", "g10", None, "low_margin"
            candidates = [lid for lid, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:3]]
            hits = []
            confidence = _clip(confidence, 0.50, 0.84)
        else:
            target = top_lid
            intent = "CROSS_LECTURE" if target != current else "CURRENT"
            mode = "cross_lecture" if target != current else "current"
            reason = "retrieval"
            nav = target != current
            hits = [h for h in hits if h["lecture"] == target][:5]

    if mode == "g10" and not candidates:
        candidates = sig.candidates or ([sig.resolved_lecture] if sig.resolved_lecture else [])
        if not candidates:
            candidates = ["D2", "D3", "D5"]
        for lid in candidates:
            labels.setdefault(lid, lecture_name(lid))

    allowed = {(h["file"], int(h["page"])) for h in hits}
    if slide_hit:
        allowed.add((slide_hit["file"], int(slide_hit["page"])))

    context_blocks = []
    for hit in hits[:5]:
        context_blocks.append(
            f"--- NGUỒN: {hit.get('doc_name')} | File: {hit['file']} | Trang: {hit['page']} ---\n{hit.get('text')}"
        )
    context = "\n\n".join(context_blocks)

    answer = ""
    citations: list[dict] = []
    invalid: list[str] = []

    if mode in ANSWER_MODES and generate_fn and context:
        system, user = _build_generate_prompt(mode, question, current, target, context, page)
        try:
            raw = generate_fn(system, user) or ""
        except Exception as exc:
            raw = ""
            answer = f"⚠️ Lỗi khi gọi mô hình: {exc}"
        if raw:
            gated, citations, invalid = _gate_refs(raw, allowed)
            answer = gated
    if not answer:
        answer = _template_answer(mode, question, current, target, hits, candidates, labels, slide_hit, reason)
        gated, citations, extra_invalid = _gate_refs(answer, allowed or {(c["file"], c["page"]) for c in _hits_to_citations(hits + ([slide_hit] if slide_hit else []))})
        invalid.extend(extra_invalid)
        if not citations:
            citations = _hits_to_citations(hits + ([slide_hit] if slide_hit else []))
        answer = gated or answer

    if mode in ("g10", "fallback"):
        citations = []
        nav = False
        if mode == "g10":
            # giữ confidence trong vùng hỏi lại
            confidence = _clip(confidence, 0.50, 0.84)

    # slide_locate luôn gắn trang viewport nếu model quên REF
    if mode == "slide_locate" and slide_hit and not citations:
        citations = _hits_to_citations([{**slide_hit, "source": "viewport"}])
        if f"[REF:{slide_hit['file']}:{slide_hit['page']}]" not in answer:
            answer = answer.rstrip() + f"\n\n[REF:{slide_hit['file']}:{slide_hit['page']}]"

    target_slide = sig.slide_num if mode == "slide_locate" and sig.slide_num else None

    result = {
        "intent": intent,
        "confidence": round(float(confidence), 3),
        "mode": mode,
        "target_lecture": target,
        "target_slide": target_slide,
        "candidates": candidates,
        "candidate_labels": {lid: labels.get(lid, lecture_name(lid)) for lid in candidates},
        "citations": citations if citation_style == "objects" else _format_eval_citations(citations),
        "citation_objects": citations,
        "invalid_citations": invalid,
        "answer": answer,
        "nav_suggestion": bool(nav and mode == "cross_lecture"),
        "needs_user_choice": mode == "g10",
        "reason": reason,
        "current_lecture": current,
        "current_page": page,
    }
    return result
