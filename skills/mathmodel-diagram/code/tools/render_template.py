#!/usr/bin/env python3
"""示意图模板统一入口（注册表驱动，见 code/templates/manifest.json）。

    python3 code/tools/render_template.py --list
    python3 code/tools/render_template.py --list --json
    python3 code/tools/render_template.py problem-flow content.json -o out.png
    python3 code/tools/render_template.py problem-flow content.json --check

id 解析顺序：manifest 中的 id → 英文别名 → 中文片段提示。
原有的逐模板调用（python3 code/templates/problem_flow.py content.json -o out.png）继续可用，
本入口只是在其上补了注册表枚举、别名解析与统一错误信息，不改变模板脚本自身的行为。

退出码：0 成功；非 0 透传模板脚本的失败码（容量校验不通过时为 1）；2 用法错误。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = SKILL_ROOT / "code" / "templates" / "manifest.json"

MSG = {
    "zh": {
        "unknown": "未知模板：{value}\n可用 id：{ids}",
        "missing_manifest": "注册表缺失或损坏：{path}",
        "missing_script": "注册表登记了不存在的脚本：{path}",
        "content_required": "渲染需要提供 content JSON 路径（--list 除外）",
    },
    "en": {
        "unknown": "Unknown template: {value}\nAvailable ids: {ids}",
        "missing_manifest": "Manifest missing or corrupt: {path}",
        "missing_script": "Manifest references a missing script: {path}",
        "content_required": "a content JSON path is required (except with --list)",
    },
}


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    """读取注册表；失败时以退出码 2 终止（用法/环境错误语义）。"""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        sys.stderr.write(MSG["zh"]["missing_manifest"].format(path=path) + "\n")
        raise SystemExit(2)


def templates(path: Path = MANIFEST_PATH) -> list[dict]:
    return load_manifest(path)["templates"]


def script_path(entry: dict, path: Path = MANIFEST_PATH) -> Path:
    """模板脚本路径：相对路径基准为注册表所在目录，再叠加 manifest 的 script_dir。"""
    base = path.parent / load_manifest(path).get("script_dir", ".")
    return (base / entry["script"]).resolve()


def normalize(value: str) -> str:
    value = value.strip().lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9\-]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def resolve_template(value: str, lang: str = "zh", path: Path = MANIFEST_PATH) -> dict:
    """id → 英文别名 → 中文片段提示，逐级回退。

    注意：normalize() 会剥离非 ASCII 字符，纯中文输入会归一化为空串。因此空 key 一律不参与
    id/别名匹配（否则会误命中"别名里含中文"的条目），中文输入只走 cjk_hints 子串匹配。
    """
    items = templates(path)
    raw, key = value.strip(), normalize(value)
    if key:
        for entry in items:
            if entry["id"] == key:
                return entry
        for entry in items:
            if key in {normalize(a) for a in entry.get("aliases", []) if normalize(a)}:
                return entry
    lowered = raw.lower()
    for entry in items:
        for hint in entry.get("cjk_hints", []):
            if hint.lower() in lowered:
                return entry
    ids = ", ".join(sorted(e["id"] for e in items))
    raise SystemExit(MSG[lang]["unknown"].format(value=value, ids=ids))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified entry for the bundled mathmodel-diagram templates.")
    parser.add_argument("template", nargs="?", help="Template id, alias, or Chinese title fragment")
    parser.add_argument("content", nargs="?", help="Path to the content JSON")
    parser.add_argument("-o", "--out", help="Output PNG path (sibling .pdf is produced too)")
    parser.add_argument("--check", action="store_true", help="Validate capacity only, write nothing")
    parser.add_argument("--list", action="store_true", help="List supported template ids")
    parser.add_argument("--json", action="store_true", help="With --list: print the manifest as JSON")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Message language")
    args = parser.parse_args()

    if args.list:
        if args.json:
            print(json.dumps(load_manifest(), ensure_ascii=False, indent=2))
        else:
            for entry in sorted(templates(), key=lambda e: e["id"]):
                print(entry["id"])
        return

    if not args.template:
        parser.error(MSG[args.lang]["content_required"])
    entry = resolve_template(args.template, args.lang)
    if not args.content:
        parser.error(MSG[args.lang]["content_required"])

    script = script_path(entry)
    if not script.exists():
        sys.stderr.write(MSG[args.lang]["missing_script"].format(path=script) + "\n")
        raise SystemExit(2)

    cmd = [sys.executable, str(script), args.content]
    if args.check:
        cmd.append("--check")
    if args.out:
        cmd += ["-o", args.out]

    result = subprocess.run(cmd, check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
