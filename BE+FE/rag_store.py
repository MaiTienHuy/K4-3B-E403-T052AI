"""Kho slide + truy xuất theo buổi. Không quyết định intent."""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

HERE = Path(__file__).resolve().parent
CONCEPT_MAP_PATH = HERE / "concept_map.json"
CHROMA_PATH = HERE / "chroma_db"
COLLECTION_NAME = "vinuni_lectures"

_TOKEN_RE = re.compile(r"[a-z0-9àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ%]+", re.I)


@lru_cache(maxsize=1)
def load_concept_map() -> dict:
    return json.loads(CONCEPT_MAP_PATH.read_text(encoding="utf-8"))


def lectures() -> dict:
    return load_concept_map()["lectures"]


def normalize_lecture(raw) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    upper = text.upper()
    if re.fullmatch(r"D[1-6]", upper):
        return upper
    match = re.search(r"(?:day|bài|bai|buổi|buoi)\s*([1-6])", text, re.I)
    if match:
        return f"D{match.group(1)}"
    match = re.search(r"day([1-6])\.pdf", text, re.I)
    if match:
        return f"D{match.group(1)}"
    catalog = lectures()
    low = text.lower()
    for lid, meta in catalog.items():
        if low == meta["file"].lower() or low == meta["name"].lower():
            return lid
    return None


def lecture_file(lid: str) -> str:
    return lectures()[lid]["file"]


def lecture_name(lid: str) -> str:
    return lectures()[lid]["name"]


def lecture_order(lid: str) -> int:
    return int(lectures()[lid]["order"])


def previous_lecture(lid: str | None) -> str | None:
    if not lid:
        return None
    current = lecture_order(lid)
    prev = None
    for other, meta in lectures().items():
        if int(meta["order"]) < current and (prev is None or int(meta["order"]) > lecture_order(prev)):
            prev = other
    return prev


def topic_index() -> str:
    lines = []
    for lid in sorted(lectures(), key=lecture_order):
        meta = lectures()[lid]
        lines.append(f"- {lid} {meta['name']}: {meta['blurb']}")
    return "\n".join(lines)


def tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in _TOKEN_RE.findall(text or "")]


def _slide_json_path(lid: str) -> Path:
    return HERE / f"day{lid[1:]}_rag.json"


def load_json_slides(lid: str) -> list[dict]:
    path = _slide_json_path(lid)
    if not path.exists():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for row in rows:
        out.append({
            "lecture": lid,
            "file": lecture_file(lid),
            "doc_name": lecture_name(lid),
            "page": int(row["page_index"]),
            "text": row.get("content") or "",
        })
    return out


@lru_cache(maxsize=1)
def all_json_slides() -> tuple:
    slides = []
    for lid in lectures():
        slides.extend(load_json_slides(lid))
    return tuple(slides)


def _parse_chroma_meta(meta: dict, doc_id: str = "") -> dict | None:
    meta = meta or {}
    file = meta.get("doc_file") or ""
    if not file:
        source = str(meta.get("source") or "")
        match = re.search(r"day([1-6])\.pdf", source, re.I)
        if match:
            file = f"day{match.group(1)}.pdf"
        else:
            match = re.search(r"day([1-6])", str(doc_id), re.I)
            if match:
                file = f"day{match.group(1)}.pdf"
    lid = normalize_lecture(file)
    if not lid:
        return None
    page = meta.get("page_index") or meta.get("page")
    try:
        page = int(page)
    except (TypeError, ValueError):
        return None
    return {
        "lecture": lid,
        "file": lecture_file(lid),
        "doc_name": meta.get("doc_name") or lecture_name(lid),
        "page": page,
    }


@lru_cache(maxsize=1)
def _chroma_collection():
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        return client.get_or_create_collection(name=COLLECTION_NAME)
    except Exception:
        return None


def get_page(file_or_lecture: str, page: int) -> dict | None:
    lid = normalize_lecture(file_or_lecture)
    if not lid:
        return None
    page = int(page)
    for slide in load_json_slides(lid):
        if slide["page"] == page:
            return slide
    pdf_path = HERE / "slide" / lecture_file(lid)
    if not _slide_json_path(lid).exists() and not pdf_path.exists():
        return None
    collection = _chroma_collection()
    if collection is None:
        return None
    try:
        got = collection.get(ids=[f"{lecture_file(lid)}_page_{page}"])
        if got and got.get("documents"):
            meta = _parse_chroma_meta(got["metadatas"][0], got.get("ids", [""])[0])
            if meta:
                return {**meta, "text": got["documents"][0] or ""}
    except Exception:
        pass
    try:
        got = collection.get(where={"doc_file": lecture_file(lid)})
        docs = got.get("documents") or []
        metas = got.get("metadatas") or []
        for doc, meta in zip(docs, metas):
            parsed = _parse_chroma_meta(meta)
            if parsed and parsed["page"] == page:
                return {**parsed, "text": doc or ""}
    except Exception:
        pass
    return None


def page_exists(file_or_lecture: str, page: int) -> bool:
    return get_page(file_or_lecture, page) is not None


def _lexical_score(query: str, text: str) -> float:
    q_tokens = tokenize(query)
    if not q_tokens:
        return 0.0
    hay = (text or "").lower()
    hits = sum(1 for tok in q_tokens if tok in hay)
    phrase_bonus = 0.0
    compact_q = " ".join(q_tokens)
    if len(compact_q) >= 8 and compact_q in hay:
        phrase_bonus = 2.0
    return hits / max(len(set(q_tokens)), 1) + phrase_bonus


def _chroma_hits(query: str, lecture_ids: list[str] | None, n: int) -> list[dict]:
    collection = _chroma_collection()
    if collection is None:
        return []
    kwargs = {"query_texts": [query], "n_results": max(n, 8)}
    if lecture_ids:
        files = [lecture_file(lid) for lid in lecture_ids]
        if len(files) == 1:
            kwargs["where"] = {"doc_file": files[0]}
        else:
            kwargs["where"] = {"doc_file": {"$in": files}}
    try:
        results = collection.query(**kwargs)
    except Exception:
        try:
            results = collection.query(query_texts=[query], n_results=max(n, 8))
        except Exception:
            return []
    hits = []
    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]
    dists = (results.get("distances") or [[]])[0]
    ids = (results.get("ids") or [[]])[0]
    for i, doc in enumerate(docs):
        parsed = _parse_chroma_meta(metas[i] if i < len(metas) else {}, ids[i] if i < len(ids) else "")
        if not parsed:
            continue
        if lecture_ids and parsed["lecture"] not in lecture_ids:
            continue
        dist = dists[i] if i < len(dists) else 1.0
        try:
            score = 1.0 / (1.0 + float(dist))
        except (TypeError, ValueError):
            score = 0.4
        hits.append({**parsed, "text": doc or "", "score": score, "source": "chroma"})
    return hits


def retrieve(query: str, lecture_ids: list[str] | None = None, n: int = 5) -> list[dict]:
    """Trả về hit {lecture,file,doc_name,page,text,score} đã lọc theo buổi nếu có."""
    merged: dict[tuple, dict] = {}

    def add(hit: dict):
        key = (hit["file"], int(hit["page"]))
        prev = merged.get(key)
        if prev is None or float(hit.get("score") or 0) > float(prev.get("score") or 0):
            merged[key] = hit

    for hit in _chroma_hits(query, lecture_ids, n):
        add(hit)

    allowed = set(lecture_ids) if lecture_ids else None
    for slide in all_json_slides():
        if allowed and slide["lecture"] not in allowed:
            continue
        score = _lexical_score(query, slide["text"])
        if score <= 0:
            continue
        add({**slide, "score": score, "source": "lexical"})

    ranked = sorted(merged.values(), key=lambda h: float(h.get("score") or 0), reverse=True)
    return ranked[:n]


def lecture_scores(hits: list[dict]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for hit in hits:
        lid = hit["lecture"]
        scores[lid] = max(scores.get(lid, 0.0), float(hit.get("score") or 0))
    return scores


def retrieval_margin(scores: dict[str, float]) -> float:
    if not scores:
        return 0.0
    ordered = sorted(scores.values(), reverse=True)
    if len(ordered) == 1:
        return 1.0
    return max(0.0, ordered[0] - ordered[1])
