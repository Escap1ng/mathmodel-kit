#!/usr/bin/env python3
"""数据图表模板渲染器（注册表驱动，见 code/tools/manifest.json）。

    python3 code/tools/render_template.py <id|别名|中文片段>
    python3 code/tools/render_template.py <id> --theme nature          # 或 --theme ./my.theme.json
    python3 code/tools/render_template.py --list [--json] / --list-themes

模板注册信息（脚本名、别名、中文提示、预览路径）全部来自 manifest.json，新增模板只需在
清单里登记一行；配色来自 themes/*.theme.json（契约见 themes/theme.schema.json），渲染时会把
所选主题写入工作区 scripts/theme.json，因此工作区自包含、改副本即可覆盖配色。

渲染行为（复制脚本 → 必要时附带 plot_style.py → 写入主题 → 运行 → 写工作区 README）与产物路径保持不变。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"
THEMES_DIR = SKILL_ROOT / "themes"
DEFAULT_THEME = "nature"

MSG = {
    "zh": {
        "unknown": "未知模板：{value}\n可用 id：{ids}",
        "missing_manifest": "注册表缺失或损坏：{path}",
        "missing_script": "打包脚本缺失：{path}",
        "missing_style": "打包样式模块缺失：{path}",
        "template_required": "需要提供模板 id（或用 --list 查看全部）",
        "theme_applied": "已应用主题：{theme} → {path}",
        "theme_unknown": "未知主题：{value}\n可用主题：{names}",
        "theme_missing": "主题文件不存在：{value}",
        "readme_title": "# 绘图复刻",
        "readme_from": "由 mathmodel-figure 技能内置模板生成。",
        "readme_outputs": "产物：",
        "copied_script": "已复制模板脚本：{path}",
        "using_existing": "使用工作区已有脚本：{path}",
        "copied_style": "已复制样式模块：{path}",
    },
    "en": {
        "unknown": "Unknown template: {value}\nAvailable ids: {ids}",
        "missing_manifest": "Manifest missing or corrupt: {path}",
        "missing_script": "Bundled script missing: {path}",
        "missing_style": "Bundled style module missing: {path}",
        "template_required": "a template is required (use --list to see all ids)",
        "theme_applied": "Applied theme: {theme} → {path}",
        "theme_unknown": "Unknown theme: {value}\nAvailable themes: {names}",
        "theme_missing": "Theme file not found: {value}",
        "readme_title": "# Figure replica",
        "readme_from": "Generated from the bundled mathmodel-figure template skill.",
        "readme_outputs": "Outputs:",
        "copied_script": "Copied template script: {path}",
        "using_existing": "Using existing workspace script: {path}",
        "copied_style": "Copied style module: {path}",
    },
}


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
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


def list_themes() -> list[tuple[str, Path]]:
    """内置主题（themes/*.theme.json），按名排序。"""
    return sorted(((p.name.removesuffix(".theme.json"), p) for p in THEMES_DIR.glob("*.theme.json")),
                  key=lambda item: item[0])


def resolve_theme(value: str | None, lang: str) -> tuple[Path | None, str]:
    """把 --theme 的取值解析为 (主题文件, 主题名)。

    不传时用内置默认主题（文件缺失则返回 None：plot_style 内部还有一层兜底，不阻断渲染）；
    传名按 themes/<name>.theme.json 查，传路径（含分隔符或以 .json 结尾）直接当文件用。
    取不到主题属用法错误，按统一退出码语义以 2 退出。
    """
    if value is None:
        path = THEMES_DIR / f"{DEFAULT_THEME}.theme.json"
        return (path, DEFAULT_THEME) if path.exists() else (None, "")

    looks_like_path = value.endswith(".json") or "/" in value or "\\" in value
    if looks_like_path:
        candidate = Path(value).expanduser().resolve()
        if not candidate.exists():
            sys.stderr.write(MSG[lang]["theme_missing"].format(value=value) + "\n")
            raise SystemExit(2)
        return candidate, candidate.name.removesuffix(".theme.json")

    path = THEMES_DIR / f"{value}.theme.json"
    if not path.exists():
        names = ", ".join(name for name, _ in list_themes()) or "-"
        sys.stderr.write(MSG[lang]["theme_unknown"].format(value=value, names=names) + "\n")
        raise SystemExit(2)
    return path, value


def normalize(value: str) -> str:
    value = value.strip().lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9\-]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def resolve_template(value: str, lang: str = "zh", path: Path = MANIFEST_PATH) -> dict:
    """id → 英文别名 → 中文图题片段，逐级回退（与历史行为一致）。

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


def write_readme(project: Path, template_id: str, script_path: Path, lang: str) -> None:
    readme = project / "README.md"
    output_stem = project / "outputs" / f"{script_path.stem.removeprefix('make_')}_replica"
    block = f"""
## {template_id}

{MSG[lang]['readme_from']}

```bash
python3 {script_path.as_posix()}
```

{MSG[lang]['readme_outputs']}

- `{output_stem.with_suffix('.png').as_posix()}`
- `{output_stem.with_suffix('.pdf').as_posix()}`
- `{output_stem.with_suffix('.svg').as_posix()}`
""".strip()
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        if f"## {template_id}" in text:
            return
        readme.write_text(text.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
    else:
        readme.write_text(MSG[lang]["readme_title"] + "\n\n" + block + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a bundled mathmodel-figure template.")
    parser.add_argument("template", nargs="?", help="Template id, alias, or Chinese title fragment")
    parser.add_argument("--project", default=None,
                        help="Output project directory (default: 绘图复刻 / figure-replica by --lang)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing copied workspace script")
    parser.add_argument("--list", action="store_true", help="List supported template ids")
    parser.add_argument("--json", action="store_true", help="With --list: print the manifest as JSON")
    parser.add_argument("--theme", default=None,
                        help="Theme name (see --list-themes) or path to a .theme.json; default: nature")
    parser.add_argument("--list-themes", action="store_true", help="List bundled theme names")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Message language")
    args = parser.parse_args()

    if args.list_themes:
        for name, _ in list_themes():
            print(name)
        return
    if args.list:
        if args.json:
            print(json.dumps(load_manifest(), ensure_ascii=False, indent=2))
        else:
            for entry in sorted(templates(), key=lambda e: e["id"]):
                print(entry["id"])
        return
    if not args.template:
        parser.error(MSG[args.lang]["template_required"])

    entry = resolve_template(args.template, args.lang)
    src = script_path(entry)
    if not src.exists():
        sys.stderr.write(MSG[args.lang]["missing_script"].format(path=src) + "\n")
        raise SystemExit(2)

    project = Path(args.project or ("绘图复刻" if args.lang == "zh" else "figure-replica"))
    project = project.expanduser().resolve()
    scripts_dir = project / "scripts"
    outputs_dir = project / "outputs"
    mpl_dir = project / ".mplconfig"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    mpl_dir.mkdir(parents=True, exist_ok=True)

    dst = scripts_dir / src.name
    if dst.exists() and not args.overwrite:
        print(MSG[args.lang]["using_existing"].format(path=dst))
    else:
        shutil.copy2(src, dst)
        print(MSG[args.lang]["copied_script"].format(path=dst))

    # 依赖统一样式模块的模板，把 plot_style.py 一并复制进工作区 scripts/
    if "from plot_style import" in src.read_text(encoding="utf-8"):
        style_src = SKILL_ROOT / "code" / "style" / "plot_style.py"
        if not style_src.exists():
            sys.stderr.write(MSG[args.lang]["missing_style"].format(path=style_src) + "\n")
            raise SystemExit(2)
        shutil.copy2(style_src, scripts_dir / "plot_style.py")
        print(MSG[args.lang]["copied_style"].format(path=scripts_dir / "plot_style.py"))

    # 主题写入工作区：plot_style.py 会优先读取同目录 theme.json，改副本即可覆盖配色
    theme_path, theme_name = resolve_theme(args.theme, args.lang)
    if theme_path is not None:
        shutil.copy2(theme_path, scripts_dir / "theme.json")
        print(MSG[args.lang]["theme_applied"].format(theme=theme_name, path=scripts_dir / "theme.json"))

    result = subprocess.run([sys.executable, str(dst)], cwd=str(project), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    write_readme(project, entry["id"], dst, args.lang)

    stem = dst.stem.removeprefix("make_")
    for suffix in (".png", ".pdf", ".svg"):
        print(outputs_dir / f"{stem}_replica{suffix}")


if __name__ == "__main__":
    main()
