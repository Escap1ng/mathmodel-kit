#!/usr/bin/env python3
"""图表主题校验器（契约见 themes/theme.schema.json）。

    python3 code/tools/validate_theme.py --all                      # 校验 themes/ 下全部主题
    python3 code/tools/validate_theme.py my-theme.theme.json        # 校验单个主题文件
    python3 code/tools/validate_theme.py --list                     # 列出内置主题名

优先使用 jsonschema（Draft 2020-12）做完整校验；未安装时降级为内置的结构校验
（必备字段、色值格式、name 规范、同目录重名），并打印提示。

退出码：0 全部通过；1 存在校验失败；2 用法或环境错误（与 strip_invisible.py / validate_content.py 语义一致）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = SKILL_ROOT / "themes"
SCHEMA_PATH = THEMES_DIR / "theme.schema.json"
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

MSG = {
    "zh": {
        "fallback": "提示：未安装 jsonschema，已降级为内置结构校验（pip install jsonschema 可获完整校验）",
        "pass": "通过：{name}",
        "fail": "失败：{name}（{count} 处）",
        "summary": "共 {total} 项，通过 {ok}，失败 {bad}",
        "schema_missing": "主题契约缺失：{path}",
        "missing": "文件不存在",
        "bad_json": "JSON 解析失败",
        "duplicate": "主题名重复：{name} 同时出现在 {files}",
        "none": "themes/ 下没有主题文件",
    },
    "en": {
        "fallback": "Note: jsonschema is not installed; falling back to the built-in structural check",
        "pass": "PASS: {name}",
        "fail": "FAIL: {name} ({count} issue(s))",
        "summary": "{total} checked, {ok} passed, {bad} failed",
        "schema_missing": "Theme schema missing: {path}",
        "missing": "file not found",
        "bad_json": "invalid JSON",
        "duplicate": "duplicate theme name: {name} appears in {files}",
        "none": "no theme files under themes/",
    },
}

REQUIRED_PATHS = {
    "roles.identity": ["main", "main_light", "main_pale", "accents"],
    "roles.baseline": ["base", "dark"],
    "roles.signal": ["positive", "negative"],
    "roles.neutral": ["bg", "light", "mid", "dark", "ink"],
}


def load_json(path: Path) -> tuple[object | None, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), ""
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"bad_json: {exc}"
    except OSError as exc:
        return None, f"missing: {exc}"


def structural_errors(theme: object) -> list[str]:
    """内置最小校验：必备字段、色值格式、色图端点数量。"""
    errors: list[str] = []
    if not isinstance(theme, dict):
        return ["$: 主题必须是 JSON 对象"]

    for key in ("schema_version", "name", "title", "roles", "cmaps"):
        if key not in theme:
            errors.append(f"$: 缺少必备字段 {key}")
    name = theme.get("name")
    if isinstance(name, str) and not NAME_RE.match(name):
        errors.append(f"$.name: {name!r} 需为小写字母/数字/连字符（供 --theme 按名解析）")

    roles = theme.get("roles")
    if not isinstance(roles, dict):
        errors.append("$.roles: 必须为对象")
    else:
        for group, fields in REQUIRED_PATHS.items():
            node = roles.get(group.split(".")[1])
            if not isinstance(node, dict):
                errors.append(f"$.{group}: 必须为对象")
                continue
            for field in fields:
                value = node.get(field)
                if value is None:
                    errors.append(f"$.{group}.{field}: 缺少必备字段")
                elif field == "accents":
                    if not isinstance(value, list) or not value:
                        errors.append(f"$.{group}.{field}: 必须为非空数组")
                    else:
                        errors += [f"$.{group}.{field}[{i}]: 色值需为 #RRGGBB，实际 {v!r}"
                                   for i, v in enumerate(value) if not (isinstance(v, str) and HEX_RE.match(v))]
                elif not (isinstance(value, str) and HEX_RE.match(value)):
                    errors.append(f"$.{group}.{field}: 色值需为 #RRGGBB，实际 {value!r}")

    cmaps = theme.get("cmaps")
    if not isinstance(cmaps, dict):
        errors.append("$.cmaps: 必须为对象")
    else:
        for field, minimum in (("divergent", 3), ("sequential", 2)):
            stops = cmaps.get(field)
            if not isinstance(stops, list) or len(stops) < minimum:
                errors.append(f"$.cmaps.{field}: 需至少 {minimum} 个色标")
            else:
                errors += [f"$.cmaps.{field}[{i}]: 色值需为 #RRGGBB，实际 {v!r}"
                           for i, v in enumerate(stops) if not (isinstance(v, str) and HEX_RE.match(v))]
    return errors


def jsonschema_errors(theme: object, schema: dict) -> list[str] | None:
    """有 jsonschema 时返回完整校验结果；未安装返回 None 表示需要降级。"""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return None
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '$'}: {e.message}"
            for e in Draft202012Validator(schema).iter_errors(theme)]


def has_jsonschema() -> bool:
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate mathmodel-figure theme files.")
    parser.add_argument("paths", nargs="*", help="Theme files to validate; omit with --all/--list")
    parser.add_argument("--all", action="store_true", help="Validate every theme under themes/")
    parser.add_argument("--list", action="store_true", help="List bundled theme names")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Message language")
    args = parser.parse_args()

    lang = args.lang
    bundled = sorted(THEMES_DIR.glob("*.theme.json"))
    if args.list:
        for path in bundled:
            theme, _ = load_json(path)
            print(theme.get("name", path.stem) if isinstance(theme, dict) else path.stem)
        return

    if args.all:
        targets = bundled
    elif args.paths:
        targets = [Path(p).expanduser().resolve() for p in args.paths]
    else:
        parser.error("provide theme file paths, or --all, or --list")
        return

    if not targets:
        print(MSG[lang]["none"])
        raise SystemExit(1)

    schema, schema_err = load_json(SCHEMA_PATH)
    if schema is None:
        print(MSG[lang]["schema_missing"].format(path=SCHEMA_PATH))
        raise SystemExit(2)
    if jsonschema_errors is not None and not has_jsonschema():
        print(MSG[lang]["fallback"])

    passed = failed = 0
    seen: dict[str, Path] = {}
    for path in targets:
        theme, err = load_json(path)
        if theme is None:
            failed += 1
            print(MSG[lang]["fail"].format(name=path.name, count=1))
            print("  -", MSG[lang].get(err.split(":")[0].strip(), err))
            continue

        errors = jsonschema_errors(theme, schema)
        if errors is None:
            errors = structural_errors(theme)

        name = theme.get("name") if isinstance(theme, dict) else None
        if isinstance(name, str):
            # 文件名与 name 必须一致，否则 --theme <name> 解析不到（nature.theme.json ↔ "nature"）
            expected_stem = path.name.removesuffix(".theme.json")
            if path.name.endswith(".theme.json") and expected_stem != name:
                errors.append(f"$.name: {name!r} 与文件名 {path.name!r} 不一致（应为 {expected_stem!r} 或改名文件）")
            if name in seen:
                errors.append(MSG[lang]["duplicate"].format(name=name, files=f"{seen[name].name}, {path.name}"))
            else:
                seen[name] = path

        if errors:
            failed += 1
            print(MSG[lang]["fail"].format(name=path.name, count=len(errors)))
            for line in errors[:10]:
                print("  -", line)
        else:
            passed += 1
            print(MSG[lang]["pass"].format(name=path.name))

    print(MSG[lang]["summary"].format(total=len(targets), ok=passed, bad=failed))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
