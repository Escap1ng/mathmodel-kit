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
import seaborn as sns
from plot_style import (COLOR_INK, DIVERGENT_CMAP, FIG_SQUARE, FS_ANNOT, FS_LABEL,
                        FS_TICK, NEUTRAL_DARK, save_fig)


def make_figure(output_stem: Path) -> None:
    """相关热力图：下三角 + 发散色图（与身份色同族：蓝→浅灰→珊红）。

    格内数值标注用常规无衬线字体、白线分隔、刻度线归零。模拟数据：6 特征 300 样本。
    """
    rng = np.random.default_rng(42)
    n = 300
    f1 = rng.normal(0, 1, n)
    f2 = 0.8 * f1 + rng.normal(0, 0.6, n)
    f3 = rng.normal(0, 1, n)
    f4 = -0.65 * f1 + 0.3 * f3 + rng.normal(0, 0.5, n)
    f5 = 0.5 * f2 + 0.4 * f4 + rng.normal(0, 0.6, n)
    f6 = rng.normal(0, 1, n)
    data = np.column_stack([f1, f2, f3, f4, f5, f6])
    labels = ["温度", "湿度", "风速", "PM2.5", "降水", "气压"]
    corr = np.corrcoef(data, rowvar=False)

    fig, ax = plt.subplots(figsize=FIG_SQUARE)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap=DIVERGENT_CMAP,
                xticklabels=labels, yticklabels=labels,
                center=0, vmin=-1, vmax=1, square=True, linewidths=0.6,
                linecolor="white", annot_kws={"fontsize": FS_ANNOT},
                cbar_kws={"shrink": 0.85, "label": "相关系数 r"}, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=FS_TICK)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=FS_TICK)
    ax.tick_params(axis="both", length=0, colors=COLOR_INK, pad=2)
    # 热图四边需闭合：保留完整细边框，与散点/折线的去上右 spine 规则有意不同
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_color(NEUTRAL_DARK)
    cbar_ax = next(a for a in fig.axes if a is not ax)   # sns.heatmap 自动绘出的色条轴
    cbar_ax.tick_params(labelsize=FS_TICK, colors=COLOR_INK, width=0.7)
    cbar_ax.yaxis.label.set_fontsize(FS_LABEL)
    cbar_ax.yaxis.label.set_color(COLOR_INK)
    ax.set_title("特征两两 Pearson 相关系数矩阵", pad=12)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "heatmap_annotated_replica")
