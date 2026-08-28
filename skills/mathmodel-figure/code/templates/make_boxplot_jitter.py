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
from plot_style import (COLOR_BASELINE, FIG_FULL, FS_ANNOT, NEUTRAL_MID,
                        identity_color, save_fig, style_axes)


def make_figure(output_stem: Path) -> None:
    """箱线图 + 抖动散点：白底箱体配身份色边框、同色粗中位线、空心菱形均值。

    个体观测以同色半透明抖动点全量呈现（Nature「显示每一次观测」原则）。模拟数据：三模型耗时分布。
    """
    rng = np.random.default_rng(0)
    names = ["模型 A（本文）", "模型 B", "模型 C"]
    data = [rng.normal(20, 3, 60), rng.normal(32, 5, 60), rng.normal(46, 8, 60)]

    fig, ax = plt.subplots(figsize=FIG_FULL)
    for i, d in enumerate(data, start=1):
        color = identity_color(i - 1)
        ax.scatter(np.full_like(d, i) + rng.uniform(-0.09, 0.09, len(d)), d, s=9,
                   color=color, alpha=0.3, edgecolors="none", zorder=2)
        ax.scatter([i], [d.mean()], marker="D", s=34, facecolor="white",
                   edgecolor=color, linewidth=1.2, zorder=5)
        box = ax.boxplot([d], positions=[i], patch_artist=True, widths=0.45, zorder=3,
                         boxprops=dict(facecolor="white", edgecolor=color, linewidth=1.0),
                         medianprops=dict(color=color, linewidth=2.2),
                         whiskerprops=dict(color=color, linewidth=0.9),
                         capprops=dict(color=color, linewidth=0.9),
                         flierprops=dict(marker="o", markersize=3.6, markerfacecolor=NEUTRAL_MID,
                                         markeredgecolor="none", alpha=0.8))
        for part in box["boxes"]:
            part.set_zorder(3)
    ax.text(0.98, 0.965, "◇ 均值 · 横线 中位数 · 散点 单次观测", transform=ax.transAxes,
            ha="right", va="top", fontsize=FS_ANNOT, color=COLOR_BASELINE)
    ax.set_xticks(np.arange(1, len(names) + 1))
    ax.set_xticklabels(names)
    ax.set_xlim(0.5, len(names) + 0.5)
    ax.set_ylim(0, max(np.max(d) for d in data) * 1.1)
    ax.set_ylabel("求解耗时 (ms)")
    style_axes(ax, grid="y")
    ax.set_title("各模型求解耗时分布（箱体 + 抖动散点）")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "boxplot_jitter_replica")
