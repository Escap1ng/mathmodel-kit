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
from plot_style import DIVERGENT_CMAP, save_fig


def make_figure(output_stem: Path) -> None:
    """相关热力图：数值标注 + 上三角遮罩 + 发散学术低饱和色图。模拟数据：6 特征 300 样本。"""
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

    fig, ax = plt.subplots(figsize=(6.6, 5.8))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap=DIVERGENT_CMAP,
                center=0, vmin=-1, vmax=1, square=True, linewidths=0.5,
                linecolor="white", annot_kws={"fontsize": 8, "family": "Consolas"},
                cbar_kws={"shrink": 0.8, "label": "相关系数 $r$"}, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_title("特征两两 Pearson 相关系数矩阵", fontsize=13, pad=14)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "heatmap_annotated_replica")
