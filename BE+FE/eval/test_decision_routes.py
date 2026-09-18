"""Đo lớp quyết định không cần LLM — chạy: python eval/test_decision_routes.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from decision import decide
from rag_store import lecture_file


def load_cases():
    return json.loads((HERE / "golden_set_cross_lecture.json").read_text(encoding="utf-8"))


def main() -> int:
    failed = []
    for case in load_cases():
        exp = case["expected"]
        result = decide(
            case["question"],
            current_lecture=case["current_lecture"],
            current_page=int(case.get("current_page") or 1),
            generate_fn=None,
            citation_style="eval",
        )
        route_ok = (result.get("target_lecture") == exp["target_lecture"]) or (
            exp["target_lecture"] is None and exp["mode"] in ("g10", "fallback")
        )
        mode_ok = result.get("mode") == exp["mode"]
        cite_ok = (not exp["must_have_citation"]) or bool(result.get("citations"))
        # Day 1 chưa có PDF trong repo — không phạt citation khi buổi đích không có slide
        if exp.get("target_lecture") == "D1" and exp["must_have_citation"]:
            if not Path(HERE.parent / "slide" / lecture_file("D1")).exists():
                cite_ok = True
        ok = route_ok and mode_ok and cite_ok and result.get("invalid_citations") == []
        mark = "PASS" if ok else "FAIL"
        print(
            f"[{case['id']}] {mark} expect={exp['mode']}/{exp['target_lecture']} "
            f"got={result['mode']}/{result['target_lecture']} conf={result['confidence']} "
            f"cites={result.get('citations')}"
        )
        if not ok:
            failed.append(case["id"])
    # Multi-turn recovery: G9/G10 chọn lại buổi rồi trả lời trong đúng buổi đó
    recovered = decide(
        "chỉ số tự động hóa sản phẩm AI",
        current_lecture="D1",
        forced_lecture="D5",
        generate_fn=None,
        citation_style="eval",
    )
    if recovered["target_lecture"] != "D5" or recovered["mode"] != "cross_lecture":
        print(f"[REC] FAIL forced D5 got {recovered['mode']}/{recovered['target_lecture']}")
        failed.append("REC")
    else:
        print("[REC] PASS forced_lecture D5 after wrong-route / G9")

    slang_then_pick = decide(
        "bữa trước cái chi dợ",
        current_lecture="D3",
        forced_lecture="D2",
        generate_fn=None,
        citation_style="eval",
    )
    if slang_then_pick["target_lecture"] != "D2":
        print(f"[REC2] FAIL G10→D2 got {slang_then_pick['mode']}/{slang_then_pick['target_lecture']}")
        failed.append("REC2")
    else:
        print("[REC2] PASS G10 slang then user picks D2")

    print(f"\n{20 + 2 - len(failed)}/{22} pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
