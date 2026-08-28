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
from plot_style import (FS_ANNOT, FIG_FULL, annotate_bars, delta_annotation,
                        identity_color, save_fig, style_axes, tint)


def make_figure(output_stem: Path) -> None:
    """分组柱状图：指标＝身份色（蓝/橙/紫），方案＝同族明度（本文最深、对照逐级变浅）。

    柱顶数值标注 + 相对本文方案的有向增益（↑绿 ↓红，仅用于表达升降）。模拟数据：三方案三指标。
    """
    groups = ["方案A（本文）", "方案B", "方案C"]
    metrics = ["准确率", "召回率", "F1"]
    data = np.array([[0.92, 0.88, 0.90], [0.85, 0.83, 0.84], [0.88, 0.90, 0.89]])
    tiers = [0.0, 0.25, 0.45]          # 明度层级：0 原色，越大越浅
    n_g, n_m = data.shape
    bar_w = 0.72 / n_m

    fig, ax = plt.subplots(figsize=FIG_FULL)
    for i in range(n_m):
        base = identity_color(i)
        centers = np.arange(n_g) + (i - (n_m - 1) / 2) * bar_w
        bars = ax.bar(centers, data[:, i], width=bar_w,
                      color=[tint(base, tiers[g]) for g in range(n_g)],
                      edgecolor="white", linewidth=0.8)
        bars[0].set_label(metrics[i])   # 每指标只取首柱作图例句柄，避免重复条目
    annotate_bars(ax, [b for c in ax.containers for b in c], fmt="{:.2f}")
    for g in range(1, n_g):             # 对照组相对本文方案的均值增益（方向色保留用法）
        text, color = delta_annotation(data[0].mean(), data[g].mean())
        ax.text(g, data[g].max() + 0.09, f"{text} vs 本文", ha="center", va="bottom",
                fontsize=FS_ANNOT, color=color)
    ax.set_xticks(np.arange(n_g))
    ax.set_xticklabels(groups)
    ax.set_ylim(0, data.max() * 1.32)
    ax.set_ylabel("指标值")
    style_axes(ax, grid="y")
    ax.legend(ncols=3, loc="upper center", bbox_to_anchor=(0.5, 1.0))
    ax.set_title("三方案综合性能指标对比")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "grouped_bar_replica")
