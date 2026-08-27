#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_MAP = {
    "multiclass-shap-combo": "make_multiclass_shap_combo.py",
    "paired-raincloud": "make_paired_raincloud.py",
    "cv-roc-ci": "make_cv_roc_ci.py",
    "taylor-diagram": "make_taylor_diagram.py",
    "correlation-pairgrid": "make_correlation_pairgrid.py",
    "prediction-marginal-grid": "make_prediction_marginal_grid.py",
    "rf-tpe-surface": "make_rf_tpe_surface.py",
    "grouped-corr-split-violin": "make_grouped_corr_split_violin.py",
    "grouped-circular-heatmap": "make_grouped_circular_heatmap.py",
    "urban-park-cooling-combo": "make_urban_park_cooling_combo.py",
    "nature-chord-diagram": "make_nature_chord_diagram.py",
    "surface-3d": "make_surface_3d.py",
    "heatmap-annotated": "make_heatmap_annotated.py",
    "fit-conf-residual": "make_fit_confidence_residual.py",
    "convergence-curve": "make_convergence_curve.py",
    "pareto-front": "make_pareto_front.py",
    "line-compare": "make_line_compare.py",
    "grouped-bar": "make_grouped_bar.py",
    "boxplot-jitter": "make_boxplot_jitter.py",
    "pie-modules": "make_pie_modules.py",
    "hbar-longlabel": "make_hbar_longlabel.py",
}

ALIASES = {
    "shap": "multiclass-shap-combo",
    "multiclass-shap": "multiclass-shap-combo",
    "raincloud": "paired-raincloud",
    "roc": "cv-roc-ci",
    "cv-roc": "cv-roc-ci",
    "taylor": "taylor-diagram",
    "pairgrid": "correlation-pairgrid",
    "correlation": "correlation-pairgrid",
    "pred-true": "prediction-marginal-grid",
    "prediction": "prediction-marginal-grid",
    "surface": "rf-tpe-surface",
    "tpe": "rf-tpe-surface",
    "split-violin": "grouped-corr-split-violin",
    "circular-heatmap": "grouped-circular-heatmap",
    "urban-cooling": "urban-park-cooling-combo",
    "chord": "nature-chord-diagram",
    "circos": "nature-chord-diagram",
    "3d-surface": "surface-3d",
    "heatmap": "heatmap-annotated",
    "fitting": "fit-conf-residual",
    "convergence": "convergence-curve",
    "pareto": "pareto-front",
    "line": "line-compare",
    "bar": "grouped-bar",
    "boxplot": "boxplot-jitter",
    "pie": "pie-modules",
    "hbar": "hbar-longlabel",
}

CJK_HINTS = {
    "多分类": "multiclass-shap-combo",
    "shap": "multiclass-shap-combo",
    "云雨": "paired-raincloud",
    "roc": "cv-roc-ci",
    "泰勒": "taylor-diagram",
    "相关矩阵组合": "correlation-pairgrid",
    "拟合线": "correlation-pairgrid",
    "预测": "prediction-marginal-grid",
    "真实": "prediction-marginal-grid",
    "tpe": "rf-tpe-surface",
    "三维曲面": "surface-3d",
    "热力图": "heatmap-annotated",
    "置信带": "fit-conf-residual",
    "残差": "fit-conf-residual",
    "收敛": "convergence-curve",
    "帕累托": "pareto-front",
    "pareto": "pareto-front",
    "折线": "line-compare",
    "柱状": "grouped-bar",
    "箱线": "boxplot-jitter",
    "饼": "pie-modules",
    "条形": "hbar-longlabel",
    "曲面": "rf-tpe-surface",
    "半边小提琴": "grouped-corr-split-violin",
    "环形热图": "grouped-circular-heatmap",
    "城市公园": "urban-park-cooling-combo",
    "堆叠": "urban-park-cooling-combo",
    "和弦": "nature-chord-diagram",
    "circos": "nature-chord-diagram",
}


def normalize(value: str) -> str:
    value = value.strip().lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9\-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def resolve_template(value: str) -> str:
    raw = value.strip()
    key = normalize(raw)
    if key in SCRIPT_MAP:
        return key
    if key in ALIASES:
        return ALIASES[key]
    lowered = raw.lower()
    for hint, template_id in CJK_HINTS.items():
        if hint.lower() in lowered:
            return template_id
    raise SystemExit(
        f"Unknown template: {value}\nAvailable ids: " + ", ".join(sorted(SCRIPT_MAP))
    )


def write_readme(project: Path, template_id: str, script_path: Path) -> None:
    readme = project / "README.md"
    output_stem = project / "outputs" / f"{script_path.stem.removeprefix('make_')}_replica"
    block = f"""
## {template_id}

Generated from the bundled mathmodel-figure template skill.

```bash
python3 {script_path.as_posix()}
```

Outputs:

- `{output_stem.with_suffix('.png').as_posix()}`
- `{output_stem.with_suffix('.pdf').as_posix()}`
- `{output_stem.with_suffix('.svg').as_posix()}`
""".strip()
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        marker = f"## {template_id}"
        if marker in text:
            return
        readme.write_text(text.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
    else:
        readme.write_text("# 绘图复刻\n\n" + block + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a bundled mathmodel-figure template.")
    parser.add_argument("template", nargs="?", help="Template id, alias, or Chinese title fragment")
    parser.add_argument("--project", default="绘图复刻", help="Output project directory, default: 绘图复刻")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing copied workspace script")
    parser.add_argument("--list", action="store_true", help="List supported template ids")
    args = parser.parse_args()

    if args.list:
        for template_id in sorted(SCRIPT_MAP):
            print(template_id)
        return
    if not args.template:
        parser.error("template is required unless --list is used")

    template_id = resolve_template(args.template)
    skill_root = Path(__file__).resolve().parents[2]
    src = skill_root / "code" / "templates" / SCRIPT_MAP[template_id]
    if not src.exists():
        raise SystemExit(f"Bundled script missing: {src}")

    project = Path(args.project).expanduser().resolve()
    scripts_dir = project / "scripts"
    outputs_dir = project / "outputs"
    mpl_dir = project / ".mplconfig"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    mpl_dir.mkdir(parents=True, exist_ok=True)

    dst = scripts_dir / src.name
    if dst.exists() and not args.overwrite:
        print(f"Using existing workspace script: {dst}")
    else:
        shutil.copy2(src, dst)
        print(f"Copied template script: {dst}")

    # 依赖统一样式模块的模板，把 plot_style.py 一并复制进工作区 scripts/
    if "from plot_style import" in src.read_text(encoding="utf-8"):
        style_src = skill_root / "code" / "style" / "plot_style.py"
        if not style_src.exists():
            raise SystemExit(f"Bundled style module missing: {style_src}")
        shutil.copy2(style_src, scripts_dir / "plot_style.py")
        print(f"Copied style module: {scripts_dir / 'plot_style.py'}")

    result = subprocess.run([sys.executable, str(dst)], cwd=str(project), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    write_readme(project, template_id, dst)

    stem = dst.stem.removeprefix("make_")
    for suffix in (".png", ".pdf", ".svg"):
        path = outputs_dir / f"{stem}_replica{suffix}"
        print(path)


if __name__ == "__main__":
    main()
