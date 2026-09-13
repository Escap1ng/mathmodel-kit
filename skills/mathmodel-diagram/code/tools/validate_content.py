#!/usr/bin/env python3
"""示意图 content JSON 的 Schema 校验器（契约见 code/templates/schema/*.schema.json）。

    python3 code/tools/validate_content.py problem-flow content.json   # 单个文件
    python3 code/tools/validate_content.py --all                       # 校验全部内置示例
    python3 code/tools/validate_content.py --schemas                   # 自检 Schema 文件本身

优先使用 jsonschema（Draft 2020-12）；未安装时降级为内置最小校验器（type/required/enum/
const/oneOf/anyOf/minItems/maxItems/minimum/maximum/minLength/maxLength/$ref），并打印提示。

退出码：0 全部通过；1 存在校验失败；2 用法或环境错误（与 strip_invisible.py 语义一致）。
"""
from __future__ import annotations

import argparse
import json
import operator
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_template import MANIFEST_PATH, load_manifest, resolve_template  # noqa: E402

MSG = {
    "zh": {
        "fallback": "提示：未安装 jsonschema，已降级为内置最小校验器（pip install jsonschema 可获完整校验）",
        "pass": "通过：{name}",
        "fail": "失败：{name}（{count} 处）",
        "missing": "文件不存在",
        "bad_json": "JSON 解析失败",
        "schema_ok": "Schema 自检通过：{name}",
        "schema_bad": "Schema 自检失败：{name}",
        "summary": "共 {total} 项，通过 {ok}，失败 {bad}",
    },
    "en": {
        "fallback": "Note: jsonschema is not installed; falling back to the built-in minimal validator",
        "pass": "PASS: {name}",
        "fail": "FAIL: {name} ({count} issue(s))",
        "missing": "file not found",
        "bad_json": "invalid JSON",
        "schema_ok": "Schema self-check passed: {name}",
        "schema_bad": "Schema self-check failed: {name}",
        "summary": "{total} checked, {ok} passed, {bad} failed",
    },
}

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "null": lambda v: v is None,
}
_NUMERIC_KEYWORDS = (
    ("minimum", operator.lt),
    ("maximum", operator.gt),
    ("exclusiveMinimum", operator.le),
    ("exclusiveMaximum", operator.ge),
)


def load_json(path: Path) -> tuple[object | None, str]:
    """返回 (数据, 错误原因)；成功时错误原因为空串。utf-8-sig 容忍 Windows 编辑器写入的 BOM。"""
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), ""
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"bad_json: {exc}"
    except OSError as exc:
        return None, f"missing: {exc}"


def resolve_ref(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        return {}
    node: object = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            return {}
        node = node[part]
    return node if isinstance(node, dict) else {}


def validate(instance, schema: dict, root: dict, path: str) -> list[str]:
    """内置最小校验器：返回错误列表，空列表表示通过。"""
    if not isinstance(schema, dict):
        return []
    if "$ref" in schema:
        return validate(instance, resolve_ref(schema["$ref"], root), root, path)

    errors: list[str] = []
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")
    if "oneOf" in schema:
        hits = sum(1 for branch in schema["oneOf"] if not validate(instance, branch, root, path))
        if hits != 1:
            errors.append(f"{path}: oneOf matched {hits} branch(es), expected exactly 1")
    if "anyOf" in schema:
        if not any(not validate(instance, branch, root, path) for branch in schema["anyOf"]):
            errors.append(f"{path}: no anyOf branch matched")

    expected = schema.get("type")
    if expected in _TYPE_CHECKS and not _TYPE_CHECKS[expected](instance):
        errors.append(f"{path}: expected {expected}, got {type(instance).__name__}")
        return errors

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required field '{key}'")
        for key, sub in schema.get("properties", {}).items():
            if key in instance:
                errors += validate(instance[key], sub, root, f"{path}.{key}")
    elif isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: {len(instance)} item(s) < minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: {len(instance)} item(s) > maxItems {schema['maxItems']}")
        if isinstance(schema.get("items"), dict):
            for index, value in enumerate(instance):
                errors += validate(value, schema["items"], root, f"{path}[{index}]")
    elif isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: length {len(instance)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: length {len(instance)} > maxLength {schema['maxLength']}")
    elif isinstance(instance, (int, float)) and not isinstance(instance, bool):
        for keyword, compare in _NUMERIC_KEYWORDS:
            if keyword in schema and compare(instance, schema[keyword]):
                errors.append(f"{path}: {instance} violates {keyword} {schema[keyword]}")

    return errors


def _draft_validator(schema: dict):
    """返回 Draft202012Validator；未安装 jsonschema 时返回 None。"""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return None
    return Draft202012Validator(schema)


def check_schema_file(path: Path, name: str, lang: str) -> list[str]:
    schema, err = load_json(path)
    if schema is None:
        return [f"{path}: {MSG[lang].get(err.split(':')[0].strip(), err)}"]
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return [] if isinstance(schema, dict) else [f"{path}: schema must be an object"]
    try:
        Draft202012Validator.check_schema(schema)
        return []
    except Exception as exc:                                   # noqa: BLE001 - 任何异常即视为失败
        return [f"{path}: {exc}"]


def check_content_file(schema_path: Path, content_path: Path, name: str, lang: str) -> list[str]:
    schema, serr = load_json(schema_path)
    if schema is None:
        return [f"{schema_path}: {MSG[lang].get(serr.split(':')[0].strip(), serr)}"]
    content, cerr = load_json(content_path)
    if content is None:
        return [f"{content_path}: {MSG[lang].get(cerr.split(':')[0].strip(), cerr)}"]

    validator = _draft_validator(schema)
    if validator is not None:
        return [f"{'/'.join(str(p) for p in e.absolute_path) or '$'}: {e.message}"
                for e in validator.iter_errors(content)]
    return validate(content, schema, schema, "$")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate mathmodel-diagram content JSON against its JSON Schema.")
    parser.add_argument("template", nargs="?", help="Template id or alias; omit with --all/--schemas")
    parser.add_argument("content", nargs="?", help="Path to the content JSON")
    parser.add_argument("--all", action="store_true", help="Validate every bundled example")
    parser.add_argument("--schemas", action="store_true", help="Self-check the Schema files")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Message language")
    args = parser.parse_args()

    lang = args.lang
    manifest = load_manifest()
    manifest_dir = MANIFEST_PATH.parent
    if _draft_validator({}) is None:
        print(MSG[lang]["fallback"])

    if args.schemas:
        cases = [(f"schema:{e['id']}", manifest_dir / e["schema"]) for e in manifest["templates"]]
        kind = "schema"
    elif args.all:
        cases = [(e["id"], manifest_dir / e["example"]) for e in manifest["templates"]]
        kind = "content"
    elif args.template and args.content:
        entry = resolve_template(args.template, lang)
        cases = [(entry["id"], Path(args.content).expanduser().resolve())]
        kind = "content"
    else:
        parser.error("provide <template> <content.json>, or --all, or --schemas")
        return

    passed = failed = 0
    for name, target in cases:
        if kind == "schema":
            errors = check_schema_file(target, name, lang)
        else:
            entry = next(e for e in manifest["templates"] if e["id"] == name)
            errors = check_content_file(manifest_dir / entry["schema"], target, name, lang)

        if errors:
            failed += 1
            label = MSG[lang]["schema_bad" if kind == "schema" else "fail"]
            print(label.format(name=name, count=len(errors)) if kind == "content"
                  else label.format(name=name))
            for line in errors[:10]:
                print("  -", line)
        else:
            passed += 1
            label = MSG[lang]["schema_ok" if kind == "schema" else "pass"]
            print(label.format(name=name))

    print(MSG[lang]["summary"].format(total=len(cases), ok=passed, bad=failed))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
