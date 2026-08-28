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
from plot_style import (ACCENT_ORANGE, ACCENT_PURPLE, COLOR_BASELINE, COLOR_MAIN,
                        FS_ANNOT, FIG_FULL, save_fig, style_axes)


def make_figure(output_stem: Path) -> None:
    """性能对比折线图：身份色 + 线型 + 标记三重冗余编码，线尾直接标注取代图例（Nature 直标法）。

    模拟数据：四种算法求解耗时随问题规模增长；基准（暴力搜索）恒为中灰，本文方法恒为主角蓝。
    """
    x = np.array([100, 200, 500, 1000, 2000, 4000])
    # 确定性模拟曲线（幂律增长，系数不同）
    y_main = 0.8 + 2.1e-3 * x + 1.4e-6 * x ** 1.35
    y_rf = 1.4 + 4.6e-3 * x + 2.6e-6 * x ** 1.35
    y_svm = 2.2 + 9.8e-3 * x + 4.0e-6 * x ** 1.35
    y_bf = 0.5 + 1.1e-2 * x

    series = [("本文方法", y_main, COLOR_MAIN, "-", "o", 2.2),
              ("随机森林", y_rf, ACCENT_ORANGE, "--", "s", 1.5),
              ("SVM", y_svm, ACCENT_PURPLE, "-.", "^", 1.5),
              ("暴力搜索（基准）", y_bf, COLOR_BASELINE, ":", "D", 1.5)]

    fig, ax = plt.subplots(figsize=FIG_FULL)
    for name, y, color, ls, mk, lw_ in series:
        ax.plot(x, y, color=color, linestyle=ls, marker=mk, markersize=4.5, linewidth=lw_,
                markerfacecolor="white", markeredgewidth=1.0, markeredgecolor=color, zorder=3)
        # 线尾直接标注：省去图例与数据之间的来回比对
        ax.text(x[-1] * 1.04, y[-1], name, color=color, fontsize=FS_ANNOT, va="center", ha="left")
    ax.set_xlabel("问题规模 n（个）")
    ax.set_ylabel("求解耗时 (ms)")
    ax.set_xlim(0, x.max() * 1.42)
    ax.set_ylim(0, None)
    style_axes(ax, grid="y")
    ax.set_title("各算法求解耗时随问题规模的变化")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "line_compare_replica")
