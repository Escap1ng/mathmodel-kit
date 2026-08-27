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
from plot_style import COLOR_INK, save_fig

GROUP_COLORS = ["#7F99C5", "#D38083", "#B7CAE4"]   # 组内低饱和衍生色板：柔蓝/柔红/淡蓝


def make_figure(output_stem: Path) -> None:
    """分组柱状图：多方案多指标对比，柱顶数值标注，Y 轴从 0 起。模拟数据：三方案三指标。"""
    groups = ["方案A（本文）", "方案B", "方案C"]
    metrics = ["准确率", "召回率", "F1"]
    data = np.array([[0.92, 0.88, 0.90], [0.85, 0.83, 0.84], [0.88, 0.90, 0.89]])
    n_g, n_m = data.shape
    bar_w = 0.7 / n_m

    fig, ax = plt.subplots(figsize=(6.3, 4.0))
    for i in range(n_m):
        centers = np.arange(n_g) + (i - (n_m - 1) / 2) * bar_w
        bars = ax.bar(centers, data[:, i], width=bar_w, color=GROUP_COLORS[i],
                      edgecolor="white", linewidth=0.8, label=metrics[i])
        for b, v in zip(bars, data[:, i]):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.005, f"{v:.2f}",
                    ha="center", va="bottom", fontsize=7.5, color=COLOR_INK)
    ax.set_xticks(np.arange(n_g))
    ax.set_xticklabels(groups)
    ax.set_ylim(0, data.max() * 1.15)
    ax.set_ylabel("指标值")
    ax.grid(axis="y", linestyle="--", color="lightgray", linewidth=0.6, alpha=0.8)
    ax.legend(frameon=False, fontsize=9, ncols=3, loc="upper right")
    ax.set_title("三方案综合性能指标对比", pad=12)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "grouped_bar_replica")
