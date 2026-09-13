#!/usr/bin/env python3
"""check_phrasing.py — 去 AI 痕迹检查器（降 AI 技能的第一道关：表述级）。

    python3 code/check_phrasing.py paper/paper.tex            # 只报不改，命中即退出 1
    python3 code/check_phrasing.py paper/*.tex --json         # 机器可读输出
    python3 code/check_phrasing.py --list-rules               # 查看词表与规则

规则表是数据：`code/phrasing-blacklist.json`（单一来源，加词只改它）。
`max_per_document` 是频次上限，**超出部分才算命中**——例如全文用一次「综上所述」可接受，堆砌则会被报出。

跳过范围：围栏代码块与行内代码跨度（反引号包裹）。因此规范文档里写成行内代码的反例不会被误报，
检查器可以直接扫自己所在技能的文档做自检。

退出码：0 通过；1 有命中；2 用法或环境错误（与 strip_invisible.py / validate_*.py 语义一致）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
BLACKLIST_PATH = CODE_DIR / "phrasing-blacklist.json"
TEXT_SUFFIXES = {".tex", ".md", ".txt", ".bib", ".typ"}
DEFAULT_MAX = 0

MSG = {
    "zh": {
        "missing": "词表缺失或损坏：{path}",
        "unknown_suffix": "跳过非文本文件：{path}",
        "no_files": "没有可检查的文件",
        "hit": "{path}:{line}:{col} [{rule}] {text}",
        "fix": "    → {fix}",
        "summary": "检查 {files} 个文件，命中 {hits} 处（词表：{rules} 条规则）",
        "summary_ok": "检查 {files} 个文件，未命中任何 AI 痕迹（词表：{rules} 条规则）",
        "freq": "（第 {n} 次出现，超过上限 {max}）",
        "list_header": "规则表（{count} 条）",
    },
    "en": {
        "missing": "Word list missing or corrupt: {path}",
        "unknown_suffix": "Skipping non-text file: {path}",
        "no_files": "No files to check",
        "hit": "{path}:{line}:{col} [{rule}] {text}",
        "fix": "    → {fix}",
        "summary": "Checked {files} file(s); {hits} hit(s) (word list: {rules} rules)",
        "summary_ok": "Checked {files} file(s); no AI-slop patterns found (word list: {rules} rules)",
        "freq": " (occurrence #{n}, over the limit of {max})",
        "list_header": "Word list ({count} rules)",
    },
}


def load_blacklist(lang: str) -> dict:
    try:
        data = json.loads(BLACKLIST_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.stderr.write(MSG[lang]["missing"].format(path=BLACKLIST_PATH) + f"\n{exc}\n")
        raise SystemExit(2)
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        sys.stderr.write(MSG[lang]["missing"].format(path=BLACKLIST_PATH) + "\n")
        raise SystemExit(2)
    for rule in data["rules"]:
        rule.setdefault("severity", "medium")
        rule.setdefault("max_per_document", DEFAULT_MAX)
        # 预编译：词表写错正则应报错，而不是静默跳过
        rule["_compiled"] = [re.compile(pattern) for pattern in rule["patterns"]]
    return data


def code_spans(line: str) -> list[tuple[int, int]]:
    """行内代码跨度（`...`）的区间，段内命中一律跳过。"""
    return [(m.start(), m.end()) for m in re.finditer(r"`[^`]*`", line)]


def scan_file(path: Path, rules: list[dict]) -> list[dict]:
    """返回该文件的命中列表；每条含行号、列号、规则与原文片段。"""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return []
    except UnicodeDecodeError:
        return []

    hits: list[dict] = []
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        spans = code_spans(line)
        for rule in rules:
            for pattern, regex in zip(rule["patterns"], rule["_compiled"]):
                for match in regex.finditer(line):
                    if any(start <= match.start() < end for start, end in spans):
                        continue
                    hits.append({
                        "rule": rule["id"],
                        "label": rule["label"],
                        "severity": rule["severity"],
                        "line": lineno,
                        "col": match.start() + 1,
                        "text": match.group(0),
                        "fix": rule.get("fix", ""),
                    })
    return hits


def apply_frequency_limit(hits: list[dict], rules_by_id: dict[str, dict]) -> list[dict]:
    """按规则统计总量，超出 max_per_document 的命中才保留（前面的算合规使用）。"""
    kept: list[dict] = []
    counters: dict[str, int] = {}
    for hit in hits:
        rule = rules_by_id[hit["rule"]]
        counters[hit["rule"]] = counters.get(hit["rule"], 0) + 1
        limit = rule.get("max_per_document", DEFAULT_MAX)
        if counters[hit["rule"]] > limit:
            hit["occurrence"] = counters[hit["rule"]]
            hit["max_per_document"] = limit
            kept.append(hit)
    return kept


def main() -> None:
    parser = argparse.ArgumentParser(description="Check text for AI-slop phrasing patterns.")
    parser.add_argument("paths", nargs="*", help="Files to check (.tex/.md/.txt/.bib/.typ)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--list-rules", action="store_true", help="Print the word list and exit")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Message language")
    args = parser.parse_args()
    lang = args.lang

    data = load_blacklist(lang)
    rules = data["rules"]
    rules_by_id = {rule["id"]: rule for rule in rules}

    if args.list_rules:
        if args.json:
            print(json.dumps({"title": data.get("title", ""), "rules": [
                {k: v for k, v in rule.items() if not k.startswith("_")} for rule in rules
            ]}, ensure_ascii=False, indent=2))
            return
        print(MSG[lang]["list_header"].format(count=len(rules)))
        for rule in rules:
            limit = rule.get("max_per_document", DEFAULT_MAX)
            limit_note = f"（≤{limit}/篇）" if limit else ""
            print(f"- {rule['id']:<20} {rule['label']}{limit_note}")
            print(f"    {rule.get('why', '')}")
            print(f"    改法：{rule.get('fix', '')}")
        return

    if not args.paths:
        sys.stderr.write(MSG[lang]["no_files"] + "\n")
        raise SystemExit(2)

    targets: list[Path] = []
    for raw in args.paths:
        path = Path(raw).expanduser()
        if not path.is_file():
            sys.stderr.write(MSG[lang]["unknown_suffix"].format(path=path) + "\n")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            sys.stderr.write(MSG[lang]["unknown_suffix"].format(path=path) + "\n")
            continue
        targets.append(path)

    if not targets:
        sys.stderr.write(MSG[lang]["no_files"] + "\n")
        raise SystemExit(2)

    all_hits: list[dict] = []
    for path in targets:
        for hit in apply_frequency_limit(scan_file(path, rules), rules_by_id):
            hit["path"] = str(path)
            all_hits.append(hit)

    all_hits.sort(key=lambda item: (item["path"], item["line"], item["col"]))

    if args.json:
        print(json.dumps({
            "files": len(targets),
            "rules": len(rules),
            "hits": all_hits,
        }, ensure_ascii=False, indent=2))
    else:
        for hit in all_hits:
            note = ""
            if "occurrence" in hit:
                note = MSG[lang]["freq"].format(n=hit["occurrence"], max=hit["max_per_document"])
            print(MSG[lang]["hit"].format(path=hit["path"], line=hit["line"], col=hit["col"],
                                          rule=hit["rule"], text=hit["text"]) + note)
            if hit["fix"]:
                print(MSG[lang]["fix"].format(fix=hit["fix"]))
        template = "summary" if all_hits else "summary_ok"
        print(MSG[lang][template].format(files=len(targets), hits=len(all_hits), rules=len(rules)))

    raise SystemExit(1 if all_hits else 0)


if __name__ == "__main__":
    main()
