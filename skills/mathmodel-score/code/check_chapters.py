#!/usr/bin/env python3
"""check_chapters.py — 论文章节结构自检（mathmodel-score 技能）。

    python3 code/check_chapters.py <论文文件...> [--rules cumcm|mcm] [--strict]
                                   [--json] [--list-checks] [--lang zh|en]

按 `code/chapter-checklist.json`（数据契约）核对论文的章节结构与格式规范：整理自《优秀论文自检表》
与全国大学生数学建模竞赛论文格式规范（2026 年修订稿）。可判定项自动核对，其余列为人工项。

- hard 项未过：结构性硬项缺失，先补齐再进入评分（不计分）
- soft 项未过：按 docs/rubric.md 的维度扣分表扣分
- `--strict`：soft 项未过也以退出码 1 结束（用于想一次打满的场合）

判定前会剔除 LaTeX 注释、代码块与行内代码，避免把说明文字误判为章节内容。

退出码：0 全部通过（或仅 manual/skip）/ 1 存在未过项 / 2 用法或输入错误。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = CODE_DIR / "chapter-checklist.json"
TEXT_SUFFIXES = {".tex", ".md", ".txt", ".typ"}
AUTO_TYPES = {"any", "all", "absent", "count-range", "keyword-count"}

MSG = {
    "zh": {
        "usage": "用法错误：请给出至少一个待检查的论文文件（.tex/.md/.txt/.typ）",
        "unreadable": "契约缺失或无法解析：{path}",
        "bad_contract": "契约格式错误：checks 必须是非空数组",
        "no_files": "没有可检查的文件（支持：{suffixes}）",
        "list_header": "章节结构自检项（{count} 项；hard {hard} / soft {soft} / 人工 {manual}）",
        "list_line": "- [{level}] {chapter} · {item}（{type}）",
        "file_header": "=== {path}  [规则集 {rules}] ===",
        "status_pass": "PASS",
        "status_fail": "FAIL",
        "status_manual": "人工",
        "status_skip": "跳过",
        "line": "  [{level}] {status}  {chapter} · {item}",
        "detail": "        要求：{requirement}",
        "detail_fix": "        修法：{fix}",
        "summary": "小结：hard 未过 {hard} 项，soft 未过 {soft} 项，人工待核 {manual} 项，跳过 {skip} 项",
        "summary_ok": "章节结构自检通过（hard 全部满足）。",
        "summary_bad": "章节结构自检未通过：先补齐 hard 项，再按 docs/rubric.md 对 soft 项扣分。",
    },
    "en": {
        "usage": "Usage error: pass at least one paper file (.tex/.md/.txt/.typ)",
        "unreadable": "Contract missing or unparsable: {path}",
        "bad_contract": "Invalid contract: checks must be a non-empty array",
        "no_files": "No checkable files (supported: {suffixes})",
        "list_header": "Chapter checks ({count}; hard {hard} / soft {soft} / manual {manual})",
        "list_line": "- [{level}] {chapter} · {item} ({type})",
        "file_header": "=== {path}  [ruleset {rules}] ===",
        "status_pass": "PASS",
        "status_fail": "FAIL",
        "status_manual": "MANUAL",
        "status_skip": "SKIP",
        "line": "  [{level}] {status}  {chapter} · {item}",
        "detail": "        Requirement: {requirement}",
        "detail_fix": "        Fix: {fix}",
        "summary": "Summary: {hard} hard failed, {soft} soft failed, {manual} manual, {skip} skipped",
        "summary_ok": "Chapter structure gate passed (all hard checks satisfied).",
        "summary_bad": "Chapter structure gate failed: fix hard items first, then deduct soft items per docs/rubric.md.",
    },
}


def load_contract(lang: str):
    try:
        data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(MSG[lang]["unreadable"].format(path=CONTRACT_PATH) + f"\n{exc}\n")
        raise SystemExit(2)
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        sys.stderr.write(MSG[lang]["bad_contract"] + "\n")
        raise SystemExit(2)
    for check in checks:
        check["_compiled"] = [re.compile(p, re.MULTILINE) for p in check.get("patterns", [])]
    return data, checks


def applicable(check: dict, rules: str) -> bool:
    return rules in (check.get("rules") or ["cumcm", "mcm"])


def match_count(patterns, text: str) -> int:
    return sum(1 for p in patterns if p.search(text))


def evaluate(check: dict, text: str) -> str:
    """返回 pass / fail（manual 由调用方处理）。"""
    kind = check["type"]
    patterns = check["_compiled"]
    if kind == "any":
        return "pass" if any(p.search(text) for p in patterns) else "fail"
    if kind == "all":
        return "pass" if patterns and all(p.search(text) for p in patterns) else "fail"
    if kind == "absent":
        return "pass" if not any(p.search(text) for p in patterns) else "fail"
    if kind == "count-range":
        hits = match_count(patterns, text)
        return "pass" if check.get("min", 0) <= hits <= check.get("max", 10 ** 6) else "fail"
    if kind == "keyword-count":
        total = 0
        for p in patterns:
            for m in p.finditer(text):
                total += len([w for w in re.split(r"[、，,;；·\s]+", m.group(1).strip()) if w])
                break
        return "pass" if check.get("min", 0) <= total <= check.get("max", 10 ** 6) else "fail"
    return "fail"


def preprocess(text: str, suffix: str) -> str:
    """屏蔽不计入结构判定的内容：LaTeX 注释、代码块与行内代码。

    论文正文里不会把「符号说明」「附录」这类字样写进注释或代码，但样例与模板会，
    因此先剔除这些区域，避免把说明文字当成章节本身。
    """
    if suffix == ".tex":
        return re.sub(r"(?<!\\)%.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[ \t]*(```|~~~).*?^[ \t]*\1.*?$", "", text, flags=re.MULTILINE | re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", text)


def check_file(path: Path, checks: list[dict], rules: str, lang: str) -> tuple[list[tuple], dict]:
    suffix = path.suffix.lower()
    text = preprocess(path.read_text(encoding="utf-8-sig"), suffix)
    is_tex = suffix == ".tex"
    rows: list[tuple] = []
    counts = {"hard": 0, "soft": 0, "manual": 0, "skip": 0, "pass": 0}
    for check in checks:
        if not applicable(check, rules):
            continue
        level, status = check["level"], None
        if check["type"] == "manual":
            status = "manual"
        elif check.get("tex_only") and not is_tex:
            status = "skip"
        else:
            status = evaluate(check, text)
        rows.append((check, status))
        if status == "fail":
            counts[level] += 1
        elif status == "manual":
            counts["manual"] += 1
        elif status == "skip":
            counts["skip"] += 1
        else:
            counts["pass"] += 1
    return rows, counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Chapter-structure self-check for contest papers.")
    parser.add_argument("paths", nargs="*", help="Paper files (.tex/.md/.txt/.typ)")
    parser.add_argument("--rules", choices=["cumcm", "mcm"], default="cumcm", help="Ruleset (default cumcm)")
    parser.add_argument("--strict", action="store_true", help="Soft failures also exit 1")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--list-checks", action="store_true", help="Print the contract")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Message language")
    args = parser.parse_args()
    lang = args.lang
    contract, checks = load_contract(lang)

    if args.list_checks:
        applicable_checks = [c for c in checks if applicable(c, args.rules)]
        if args.json:
            print(json.dumps([{k: v for k, v in c.items() if k != "_compiled"} for c in applicable_checks],
                             ensure_ascii=False, indent=2))
            return
        print(MSG[lang]["list_header"].format(
            count=len(applicable_checks),
            hard=sum(1 for c in applicable_checks if c["level"] == "hard"),
            soft=sum(1 for c in applicable_checks if c["level"] == "soft"),
            manual=sum(1 for c in applicable_checks if c["type"] == "manual")))
        for check in applicable_checks:
            print(MSG[lang]["list_line"].format(**check))
        return

    if not args.paths:
        sys.stderr.write(MSG[lang]["usage"] + "\n")
        raise SystemExit(2)

    files = [Path(p).expanduser() for p in args.paths]
    files = [p for p in files if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES]
    if not files:
        sys.stderr.write(MSG[lang]["no_files"].format(suffixes=", ".join(sorted(TEXT_SUFFIXES))) + "\n")
        raise SystemExit(2)

    report: dict = {"rules": args.rules, "files": []}
    hard_fail = soft_fail = 0
    for path in files:
        rows, counts = check_file(path, checks, args.rules, lang)
        hard_fail += counts["hard"]
        soft_fail += counts["soft"]
        report["files"].append({
            "path": str(path), "counts": counts,
            "checks": [{"id": c["id"], "level": c["level"], "status": s,
                        "chapter": c["chapter"], "item": c["item"]} for c, s in rows],
        })
        if args.json:
            continue
        print(MSG[lang]["file_header"].format(path=path, rules=args.rules))
        for check, status in rows:
            label = {"pass": MSG[lang]["status_pass"], "fail": MSG[lang]["status_fail"],
                     "manual": MSG[lang]["status_manual"], "skip": MSG[lang]["status_skip"]}[status]
            print(MSG[lang]["line"].format(level=check["level"], status=label,
                                           chapter=check["chapter"], item=check["item"]))
            if status == "fail":
                print(MSG[lang]["detail"].format(requirement=check.get("requirement", "")))
                print(MSG[lang]["detail_fix"].format(fix=check.get("fix", "")))
        print(MSG[lang]["summary"].format(**counts))
        print("")

    failed = hard_fail > 0 or (args.strict and soft_fail > 0)
    if args.json:
        report["hard_failed"] = hard_fail
        report["soft_failed"] = soft_fail
        report["pass"] = not failed
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif failed:
        print(MSG[lang]["summary_bad"])
    else:
        print(MSG[lang]["summary_ok"])

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
