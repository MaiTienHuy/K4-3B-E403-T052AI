"""Chạy golden set qua lớp quyết định thật (decision.decide).

Dùng:  python eval/run_eval.py
       python eval/run_eval.py --limit 3
       python eval/run_eval.py --no-llm
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOTYPE_DIR = HERE.parent
sys.path.insert(0, str(PROTOTYPE_DIR))

from dotenv import load_dotenv

from decision import decide

load_dotenv(dotenv_path=PROTOTYPE_DIR / ".env", override=True)

GOLDEN = HERE / "golden_set_cross_lecture.json"
REPORT = HERE / "report_latest.json"


def _make_generate_fn():
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    if os.environ.get("OPENROUTER_API_KEY", "").strip():
        def generate(system, user):
            import openai
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ["OPENROUTER_API_KEY"].strip(),
                default_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "VLearn Study Assistant Eval",
                },
            )
            completion = client.chat.completions.create(
                model="deepseek/deepseek-chat",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return completion.choices[0].message.content
        return generate

    def generate_gemini(system, user):
        from google import genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip())
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=f"{system}\n\n{user}",
        )
        return response.text
    return generate_gemini


def run_prototype(question: str, current_lecture: str, current_page: int = 1, generate_fn=None) -> dict:
    started = time.time()
    result = decide(
        question,
        current_lecture=current_lecture,
        current_page=current_page,
        generate_fn=generate_fn,
        citation_style="eval",
    )
    result["latency_ms"] = int((time.time() - started) * 1000)
    return result


def load_cases() -> list[dict]:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def eval_case(case: dict, generate_fn=None) -> dict:
    exp = case["expected"]
    res = run_prototype(
        case["question"],
        case["current_lecture"],
        current_page=int(case.get("current_page") or 1),
        generate_fn=generate_fn,
    )
    got_lecture = res.get("target_lecture")
    route_ok = (got_lecture == exp["target_lecture"]) or (
        exp["target_lecture"] is None and exp["mode"] in ("g10", "fallback")
    )
    mode_ok = res.get("mode") == exp["mode"]
    grounded_ok = res.get("invalid_citations", []) == []
    citation_ok = (not exp["must_have_citation"]) or bool(res.get("citations"))
    return {
        "id": case["id"],
        "question": case["question"],
        "taxonomy_class": case["taxonomy_class"],
        "expected_mode": exp["mode"],
        "got_mode": res.get("mode"),
        "got_intent": res.get("intent"),
        "confidence": res.get("confidence"),
        "target_lecture": got_lecture,
        "expected_lecture": exp.get("target_lecture"),
        "target_slide": res.get("target_slide"),
        "citations": res.get("citations"),
        "invalid_citations": res.get("invalid_citations"),
        "latency_ms": res.get("latency_ms"),
        "answer": res.get("answer"),
        "reason": res.get("reason"),
        "PASS": bool(route_ok and mode_ok and grounded_ok and citation_ok),
        "_route_ok": route_ok,
        "_mode_ok": mode_ok,
        "_citation_ok": citation_ok,
        "_grounded_ok": grounded_ok,
    }


def summarize(rows: list[dict]) -> dict:
    n = len(rows) or 1

    def rate(key):
        return round(sum(1 for r in rows if r.get(key)) / n, 4)

    return {
        "total": len(rows),
        "pass_rate": rate("PASS"),
        "routing_accuracy": rate("_route_ok"),
        "mode_accuracy": rate("_mode_ok"),
        "grounding_factuality": rate("_grounded_ok"),
        "latencies": sorted(r.get("latency_ms") or 0 for r in rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--no-llm", action="store_true", help="Chỉ đo lớp quyết định, không gọi model")
    args = parser.parse_args()

    generate_fn = None if args.no_llm else _make_generate_fn()
    cases = load_cases()
    if args.limit:
        cases = cases[: args.limit]

    rows = []
    REPORT.write_text("[]", encoding="utf-8")
    for case in cases:
        try:
            row = eval_case(case, generate_fn=generate_fn)
        except Exception as exc:
            row = {"id": case["id"], "PASS": False, "error": f"{type(exc).__name__}: {exc}"}
        rows.append(row)
        REPORT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"[{row['id']}] {'PASS' if row.get('PASS') else 'FAIL'} "
            f"mode={row.get('got_mode')} lec={row.get('target_lecture')} "
            f"conf={row.get('confidence')} reason={row.get('reason')}"
        )

    scored = [row for row in rows if "error" not in row]
    summary = summarize(scored)
    (HERE / "summary_latest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
