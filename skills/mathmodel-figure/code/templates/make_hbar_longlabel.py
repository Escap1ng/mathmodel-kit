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
from plot_style import FIG_FULL, TONE_RAMP, annotate_bars, save_fig, style_axes


def make_figure(output_stem: Path) -> None:
    """长类别横向条形图：按数值降序排名，同族明度阶梯编码名次（第一名最深、逐级变浅）。

    条端数值标注、数值轴从 0 起。模拟数据：检测模型 mAP 对比。
    """
    cats = ["YOLOv8 检测模型（本文）", "Faster R-CNN 检测模型", "SSD 检测模型", "CenterNet 检测模型"]
    vals = np.array([0.923, 0.874, 0.831, 0.796])
    order = np.argsort(vals)[::-1]      # 排名图一律降序，读者无需比对坐标
    cats, vals = [cats[i] for i in order], vals[order]
    y = np.arange(len(cats))[::-1]

    fig, ax = plt.subplots(figsize=FIG_FULL)
    bars = ax.barh(y, vals, height=0.62, color=TONE_RAMP[:len(vals)],
                   edgecolor="white", linewidth=0.8)
    annotate_bars(ax, bars, fmt="{:.3f}", orient="h")
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.set_xlim(0, vals.max() * 1.14)
    ax.set_xlabel("mAP@0.5")
    style_axes(ax, grid="x")
    ax.set_title("各检测模型精度对比")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "hbar_longlabel_replica")
