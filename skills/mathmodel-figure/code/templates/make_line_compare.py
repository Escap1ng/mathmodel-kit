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
from plot_style import COLOR_ACCENT, COLOR_MAIN, COLOR_ROCK, COLOR_SAGE, save_fig


def make_figure(output_stem: Path) -> None:
    """性能对比折线图：线型+标记冗余编码、坐标轴从 0 起、仅横向网格。模拟数据：耗时随规模增长。"""
    x = np.array([100, 200, 500, 1000, 2000, 4000])
    # 确定性模拟曲线（幂律增长，系数不同）
    y_main = 0.8 + 2.1e-3 * x + 1.4e-6 * x ** 1.35
    y_rf = 1.4 + 4.6e-3 * x + 2.6e-6 * x ** 1.35
    y_svm = 2.2 + 9.8e-3 * x + 4.0e-6 * x ** 1.35
    y_bf = 0.5 + 2.6e-2 * x

    styles = [(COLOR_MAIN, "-", "o", 2.5), (COLOR_ACCENT, "--", "s", 1.5),
              (COLOR_SAGE, "-.", "^", 1.5), (COLOR_ROCK, ":", "D", 1.5)]
    fig, ax = plt.subplots(figsize=(6.3, 4.0))
    for (color, ls, mk, lw_), (name, y) in zip(
            styles, [("本文方法", y_main), ("随机森林", y_rf), ("SVM", y_svm), ("暴力搜索", y_bf)]):
        ax.plot(x, y, color=color, linestyle=ls, marker=mk, markersize=5,
                linewidth=lw_, markerfacecolor="white", label=name)
    ax.set_xlabel("问题规模 $n$（个）")
    ax.set_ylabel("求解耗时 (ms)")
    ax.set_xlim(0, x.max() * 1.05)
    ax.set_ylim(0, None)
    ax.grid(axis="y", linestyle="--", color="lightgray", linewidth=0.6, alpha=0.8)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.set_title("各算法求解耗时随问题规模的变化", pad=12)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "line_compare_replica")
