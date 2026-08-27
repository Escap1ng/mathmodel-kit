from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _cand in (HERE, ROOT / "style"):
    if (_cand / "plot_style.py").exists():
        sys.path.insert(0, str(_cand))
        break

os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np
from plot_style import COLOR_ACCENT, COLOR_INK, COLOR_MAIN, COLOR_ROCK, COLOR_SAGE, save_fig


def make_figure(output_stem: Path) -> None:
    """长类别条形图：类别名较长时替代柱状图，数值轴从 0 起、条端标注。模拟数据：检测模型 mAP 对比。"""
    cats = ["YOLOv8 检测模型（本文）", "Faster R-CNN 检测模型", "SSD 检测模型", "CenterNet 检测模型"]
    vals = [0.923, 0.874, 0.831, 0.796]
    colors = [COLOR_MAIN, COLOR_ROCK, COLOR_SAGE, COLOR_ACCENT]

    fig, ax = plt.subplots(figsize=(6.3, 4.0))
    bars = ax.barh(np.arange(len(cats))[::-1], vals, height=0.6, color=colors,
                   edgecolor="white", linewidth=0.8)
    for b, v in zip(bars, vals):
        ax.text(v + 0.005, b.get_y() + b.get_height() / 2, f"{v:.3f}",
                va="center", ha="left", fontsize=7.5, color=COLOR_INK)
    ax.set_yticks(np.arange(len(cats))[::-1])
    ax.set_yticklabels(cats, fontsize=9)
    ax.set_xlim(0, max(vals) * 1.12)
    ax.set_xlabel("mAP@0.5")
    ax.grid(axis="x", linestyle="--", color="lightgray", linewidth=0.6, alpha=0.8)
    ax.set_title("各检测模型精度对比", pad=12)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "hbar_longlabel_replica")
