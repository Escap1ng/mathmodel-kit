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
from plot_style import COLOR_ACCENT, COLOR_INK, COLOR_MAIN, COLOR_ROCK, save_fig


def make_figure(output_stem: Path) -> None:
    """箱线图 + 抖动散点：主色箱填充、绛红中位线、岩石灰离群点。模拟数据：三模型耗时分布。"""
    rng = np.random.default_rng(0)
    data = [rng.normal(20, 3, 60), rng.normal(32, 5, 60), rng.normal(46, 8, 60)]

    fig, ax = plt.subplots(figsize=(6.3, 4.0))
    for i, d in enumerate(data, start=1):
        ax.scatter(np.full_like(d, i) + rng.uniform(-0.08, 0.08, len(d)), d,
                   s=10, color=COLOR_ROCK, alpha=0.35, edgecolors="none", zorder=2)
    ax.boxplot(data, patch_artist=True, widths=0.45, zorder=3,
               boxprops=dict(facecolor=COLOR_MAIN, alpha=0.7, color=COLOR_INK),
               medianprops=dict(color=COLOR_ACCENT, linewidth=2),
               whiskerprops=dict(color=COLOR_INK), capprops=dict(color=COLOR_INK),
               flierprops=dict(marker="o", markersize=4, markerfacecolor=COLOR_ROCK,
                               markeredgecolor="none", alpha=0.7))
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["模型1", "模型2", "模型3"])
    ax.set_xlim(0.5, 3.5)
    ax.set_ylabel("求解耗时 (ms)")
    ax.grid(axis="y", linestyle="--", color="lightgray", linewidth=0.6, alpha=0.8)
    ax.set_title("各模型求解耗时分布（箱体 + 抖动散点）", pad=12)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "boxplot_jitter_replica")
