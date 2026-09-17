"""
Test Runner cho bộ kiểm thử Golden Set (CP3)
==============================================
Chạy tự động toàn bộ 20 case trong eval/golden_set.json,
tính toán độ chính xác và xuất báo cáo kết quả.
"""

import os
import sys
import io
import json
from datetime import datetime

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from codebase.router import route_query

GOLDEN_SET_PATH = os.path.join(os.path.dirname(__file__), "golden_set.json")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "eval_results_run1.md")

def run_evaluation():
    print("=" * 70)
    print("BẮT ĐẦU CHẠY KIỂM THỬ GOLDEN SET - LƯỢT 1 (CP3)")
    print("=" * 70)

    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    total_cases = len(test_cases)
    passed_cases = 0
    results = []

    for case in test_cases:
        c_id = case["id"]
        u_input = case["user_input"]
        curr_lec = case.get("current_lecture", "Day10")
        exp_code = case.get("expected_lecture_code")
        exp_action = case.get("expected_action")

        # Gọi Router
        res = route_query(u_input, current_lecture=curr_lec)
        act_code = res.get("lecture_code")
        act_action = res.get("action")
        engine = res.get("engine", "unknown")

        # Kiểm tra điều kiện Đạt (Pass)
        code_match = (act_code == exp_code)
        action_match = (act_action == exp_action)
        is_pass = code_match and action_match

        if is_pass:
            passed_cases += 1
            status_str = "PASS"
        else:
            status_str = "FAIL"

        print(f"[{status_str}] {c_id}: '{u_input}' -> Code: {act_code} (Exp: {exp_code}) | Action: {act_action} (Exp: {exp_action})")

        results.append({
            "id": c_id,
            "input": u_input,
            "category": case.get("category"),
            "source": case.get("source"),
            "expected_code": exp_code,
            "actual_code": act_code,
            "expected_action": exp_action,
            "actual_action": act_action,
            "is_pass": is_pass,
            "explanation": res.get("explanation", ""),
            "engine": engine
        })

    pass_rate = (passed_cases / total_cases) * 100
    print("-" * 70)
    print(f"KẾT QUẢ TỔNG QUAN: {passed_cases}/{total_cases} câu đạt ({pass_rate:.1f}%)")
    print(f"Quality bar đề ra trong spec: >= 85%")
    if pass_rate >= 85:
        print("Trạng thái: ĐẠT QUALITY BAR (SHIP)")
    else:
        print("Trạng thái: CHƯA ĐẠT QUALITY BAR (Cần phân tích nguyên nhân lỗi)")
    print("-" * 70)

    # Xuất file Markdown báo cáo
    generate_markdown_report(results, total_cases, passed_cases, pass_rate)
    print(f"Đã lưu báo cáo chi tiết vào: {REPORT_PATH}")

def generate_markdown_report(results, total, passed, rate):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    engine_name = results[0]["engine"] if results else "unknown"

    md = []
    md.append("# Báo cáo đo lường chất lượng Lượt 1 (CP3)")
    md.append(f"- **Thời điểm chạy:** {now_str}")
    md.append(f"- **Engine thực thi:** `{engine_name}`")
    md.append(f"- **Tổng số test cases:** {total}")
    md.append(f"- **Số case Pass:** {passed}")
    md.append(f"- **Tỷ lệ chính xác:** **{rate:.1f}%**")
    md.append(f"- **Quality bar cam kết:** $\\ge 85\\%$")
    md.append("")
    md.append("## Bảng chi tiết kết quả từng test case")
    md.append("")
    md.append("| ID | Câu hỏi test | Lớp/Nhóm | Kỳ vọng | Thực tế | Hành vi | Trạng thái | Ghi chú / Nguyên nhân |")
    md.append("|---|---|---|---|---|---|:---:|---|")

    for r in results:
        status_icon = "✅ PASS" if r["is_pass"] else "❌ FAIL"
        exp_summary = f"`{r['expected_code']}` ({r['expected_action']})"
        act_summary = f"`{r['actual_code']}` ({r['actual_action']})"
        note = r['explanation'] if r['is_pass'] else f"Lệch: {r['explanation']}"
        md.append(f"| {r['id']} | {r['input']} | {r['category']} | {exp_summary} | {act_summary} | {r['actual_action']} | {status_icon} | {note} |")

    md.append("")
    md.append("## Phân tích nguyên nhân các case Fail (nếu có)")
    failed_cases = [r for r in results if not r["is_pass"]]
    if not failed_cases:
        md.append("- Toàn bộ 20 test cases đều đạt chuẩn.")
    else:
        for f in failed_cases:
            md.append(f"- **{f['id']}** (`{f['input']}`): Kỳ vọng `{f['expected_code']}` ({f['expected_action']}) nhưng nhận `{f['actual_code']}` ({f['actual_action']}). Nguyên nhân: {f['explanation']}")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

if __name__ == "__main__":
    run_evaluation()
