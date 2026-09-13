#!/usr/bin/env python3
"""score_card.py — 论文评分卡计算器（mathmodel-score 技能）。

    python3 code/score_card.py scorecard.json           # 校验评分卡 + 渲染评分表
    python3 code/score_card.py scorecard.json --json     # 机器可读输出
    python3 code/score_card.py --list-dimensions         # 查看维度契约（含满分）

评分口径见 `docs/rubric.md`，标准：总分 ≥ 85 且无一票否决。评分卡是数据，
可被第三方程序读取；本脚本只做校验、加权汇总与渲染，不替使用者判断扣分。

退出码：0 达标 / 1 需优化（含一票否决）/ 2 用法或输入错误（与 check_*.py、validate_*.py 语义一致）。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DIMENSIONS = [
    {"id": "abstract", "label": "摘要", "max": 30},
    {"id": "model", "label": "算法/模型正确性", "max": 20},
    {"id": "innovation", "label": "创新性", "max": 20},
    {"id": "writing", "label": "写作能力", "max": 15},
    {"id": "layout", "label": "排版", "max": 15},
]
PASS_SCORE = 85
MAX_ROUNDS = 3

MSG = {
    "zh": {
        "usage": "用法错误",
        "unreadable": "评分卡缺失或无法解析：{path}",
        "bad_shape": "评分卡格式错误：dimensions 必须是非空数组",
        "missing": "缺少维度：{ids}（见 --list-dimensions）",
        "unknown": "未知维度：{ids}",
        "bad_score": "维度 {id} 的 score 必须是 0-{max} 之间的数值，当前为 {value}",
        "duplicate": "维度重复：{ids}",
        "inconsistent": "提示：维度 {id} 的扣分合计 {sum} 与 (满分-得分) {gap} 不一致",
        "header": "========== 论文评分表 ==========",
        "col": "维度|得分|满分",
        "line": "-" * 33,
        "total_label": "总分",
        "verdict": "判定：{verdict}",
        "verdict_pass": "达标",
        "verdict_fix": "需优化",
        "verdict_veto": "一票否决（直接淘汰）",
        "details": "扣分明细：",
        "detail_line": "{n}. [{dim}] {item} -{penalty}分{note}",
        "round": "优化轮次：第 {n} 轮（熔断上限 {max} 轮）",
        "round_over": "优化轮次已达/超过熔断上限 {max} 轮，须人工复核",
        "reason_pass": "总分 {total} ≥ {pass_score}，且无一票否决",
        "reason_fix": "总分 {total} < {pass_score}，需针对性优化后重新评分",
        "reason_veto": "触发一票否决（身份信息/页眉等红线），直接淘汰、不计分",
        "list_header": "评分维度（{count} 项，满分合计 {total}）",
        "list_line": "- {id:<12} {label} 满分 {max}",
    },
    "en": {
        "usage": "Usage error",
        "unreadable": "Scorecard missing or unparsable: {path}",
        "bad_shape": "Invalid scorecard: dimensions must be a non-empty array",
        "missing": "Missing dimensions: {ids} (see --list-dimensions)",
        "unknown": "Unknown dimensions: {ids}",
        "bad_score": "Dimension {id} score must be a number in 0-{max}, got {value}",
        "duplicate": "Duplicate dimensions: {ids}",
        "inconsistent": "Note: dimension {id} deductions sum {sum} != (max-score) {gap}",
        "header": "========== Paper scorecard ==========",
        "col": "Dimension|Score|Max",
        "line": "-" * 33,
        "total_label": "Total",
        "verdict": "Verdict: {verdict}",
        "verdict_pass": "PASS",
        "verdict_fix": "NEEDS WORK",
        "verdict_veto": "VETOED (disqualified)",
        "details": "Deductions:",
        "detail_line": "{n}. [{dim}] {item} -{penalty}{note}",
        "round": "Optimization round: {n} (cap {max})",
        "round_over": "Round count reached/exceeded the cap of {max}; needs human review",
        "reason_pass": "Total {total} >= {pass_score} with no veto",
        "reason_fix": "Total {total} < {pass_score}; fix and re-score",
        "reason_veto": "Veto triggered (identity/header red line); disqualified without scoring",
        "list_header": "Score dimensions ({count}; total {total})",
        "list_line": "- {id:<12} {label} max {max}",
    },
}


def disp_len(text: str) -> int:
    """显示宽度：CJK 记 2，其余记 1。"""
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in text)


def pad_right(text: str, width: int) -> str:
    return text + " " * max(0, width - disp_len(text))


def pad_left(text: str, width: int) -> str:
    return " " * max(0, width - disp_len(text)) + text


def load_card(path: Path, lang: str) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        sys.stderr.write(MSG[lang]["unreadable"].format(path=path) + f"\n{exc}\n")
        return None


def validate(data: dict, lang: str) -> tuple[dict[str, dict], list[str]]:
    """返回 (按 id 归位的维度字典, 错误列表)。"""
    errors: list[str] = []
    dims = data.get("dimensions")
    if not isinstance(dims, list) or not dims:
        return {}, [MSG[lang]["bad_shape"]]

    contract = {d["id"]: d for d in DIMENSIONS}
    by_id: dict[str, dict] = {}
    for entry in dims:
        did = entry.get("id") if isinstance(entry, dict) else None
        if did not in contract:
            errors.append(MSG[lang]["unknown"].format(ids=did))
            continue
        if did in by_id:
            errors.append(MSG[lang]["duplicate"].format(ids=did))
            continue
        value = entry.get("score")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= contract[did]["max"]:
            errors.append(MSG[lang]["bad_score"].format(id=did, max=contract[did]["max"], value=value))
            continue
        by_id[did] = entry

    missing = [d["id"] for d in DIMENSIONS if d["id"] not in by_id]
    if missing:
        errors.append(MSG[lang]["missing"].format(ids=", ".join(missing)))
    return by_id, errors


def collect_deductions(by_id: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    for dim in DIMENSIONS:
        entry = by_id.get(dim["id"])
        if not entry:
            continue
        for item in entry.get("deductions", []) or []:
            out.append({
                "dim": dim["label"],
                "dim_id": dim["id"],
                "item": item.get("item", ""),
                "penalty": item.get("penalty", 0),
                "note": item.get("note", ""),
            })
    out.sort(key=lambda d: (-float(d["penalty"] or 0)))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and render a paper scorecard.")
    parser.add_argument("scorecard", nargs="?", help="Scorecard JSON file")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--list-dimensions", action="store_true", help="Print the dimension contract")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Message language")
    args = parser.parse_args()
    lang = args.lang

    if args.list_dimensions:
        total = sum(d["max"] for d in DIMENSIONS)
        if args.json:
            print(json.dumps({"pass_score": PASS_SCORE, "max_rounds": MAX_ROUNDS,
                              "dimensions": DIMENSIONS}, ensure_ascii=False, indent=2))
            return
        print(MSG[lang]["list_header"].format(count=len(DIMENSIONS), total=total))
        for dim in DIMENSIONS:
            print(MSG[lang]["list_line"].format(**dim))
        return

    if not args.scorecard:
        sys.stderr.write(MSG[lang]["usage"] + "\n")
        raise SystemExit(2)

    path = Path(args.scorecard).expanduser()
    if not path.is_file():
        sys.stderr.write(MSG[lang]["unreadable"].format(path=path) + "\n")
        raise SystemExit(2)

    data = load_card(path, lang)
    if data is None:
        raise SystemExit(2)
    by_id, errors = validate(data, lang)
    if errors:
        for line in errors:
            sys.stderr.write(line + "\n")
        raise SystemExit(2)

    veto = bool(data.get("veto"))
    round_no = data.get("round")
    total = sum(by_id[d["id"]]["score"] for d in DIMENSIONS)
    verdict = ("veto" if veto else "pass" if total >= PASS_SCORE else "fix")
    passed = verdict == "pass"

    for dim in DIMENSIONS:  # 扣分合计与得分的自洽性提示（不失败）
        entry = by_id[dim["id"]]
        penalties = sum(float(i.get("penalty", 0) or 0) for i in entry.get("deductions", []) or [])
        gap = dim["max"] - entry["score"]
        if penalties and abs(penalties - gap) > 1e-6:
            sys.stderr.write(MSG[lang]["inconsistent"].format(id=dim["id"], sum=penalties, gap=gap) + "\n")

    deductions = collect_deductions(by_id)
    if args.json:
        print(json.dumps({
            "paper": data.get("paper", ""), "round": round_no, "veto": veto,
            "total": total, "max": sum(d["max"] for d in DIMENSIONS),
            "pass_score": PASS_SCORE, "pass": passed, "verdict": verdict,
            "dimensions": [{"id": d["id"], "label": d["label"],
                            "score": by_id[d["id"]]["score"], "max": d["max"]} for d in DIMENSIONS],
            "deductions": deductions,
        }, ensure_ascii=False, indent=2))
        raise SystemExit(0 if passed else 1)

    print(MSG[lang]["header"])
    if data.get("paper"):
        print(pad_right(str(data["paper"]), 33))
    print(pad_right(MSG[lang]["col"].split("|")[0], 16)
          + pad_left(MSG[lang]["col"].split("|")[1], 8)
          + pad_left(MSG[lang]["col"].split("|")[2], 8))
    print(MSG[lang]["line"])
    for dim in DIMENSIONS:
        print(pad_right(dim["label"], 16)
              + pad_left(str(by_id[dim["id"]]["score"]), 8)
              + pad_left(str(dim["max"]), 8))
    print(MSG[lang]["line"])
    print(pad_right(MSG[lang]["total_label"], 16)
          + pad_left(str(total), 8)
          + pad_left("100", 8))
    print(MSG[lang]["line"])
    verdict_key = {"pass": "verdict_pass", "fix": "verdict_fix", "veto": "verdict_veto"}[verdict]
    print(MSG[lang]["verdict"].format(verdict=MSG[lang][verdict_key]))
    if isinstance(round_no, int):
        print(MSG[lang]["round"].format(n=round_no, max=MAX_ROUNDS))
        if round_no > MAX_ROUNDS:
            print(MSG[lang]["round_over"].format(max=MAX_ROUNDS))
    print(MSG[lang]["details"])
    for i, item in enumerate(deductions, start=1):
        note = f"：{item['note']}" if item["note"] else ""
        print(MSG[lang]["detail_line"].format(n=i, dim=item["dim"], item=item["item"],
                                              penalty=item["penalty"], note=note))
    reason_key = {"pass": "reason_pass", "fix": "reason_fix", "veto": "reason_veto"}[verdict]
    print(MSG[lang][reason_key].format(total=total, pass_score=PASS_SCORE))
    print("=" * 33)

    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
