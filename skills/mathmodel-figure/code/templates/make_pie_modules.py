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
from plot_style import COLOR_INK, FIG_FULL, FS_ANNOT, NEUTRAL_MID, TONE_RAMP, save_fig


def make_figure(output_stem: Path) -> None:
    """模块占比环形图：≤5 类、白色分隔线，占比大小由同族明度编码（最大块最深）。

    类别与百分比用引线直接标注在环外，取消图例。模拟数据：求解管线耗时构成。
    """
    labels = ["特征提取", "模型推理", "数据加载", "其他"]
    sizes = [52, 30, 12, 6]

    fig, ax = plt.subplots(figsize=FIG_FULL)
    wedges, _ = ax.pie(
        sizes, colors=TONE_RAMP[:len(sizes)], startangle=90, counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=1.2))
    for wedge, label, pct in zip(wedges, labels, sizes):
        angle = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
        x, y = np.cos(angle), np.sin(angle)
        ax.annotate(f"{label}\n{pct:.1f}%", xy=(x * 1.0, y * 1.0), xytext=(x * 1.32, y * 1.32),
                    ha="left" if x >= 0 else "right", va="center", fontsize=FS_ANNOT,
                    color=COLOR_INK, linespacing=1.3,
                    arrowprops=dict(arrowstyle="-", color=NEUTRAL_MID, linewidth=0.7,
                                    shrinkA=0, shrinkB=2))
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.35, 1.35)
    ax.set_title("求解管线各模块耗时占比", pad=12)
    ax.set_aspect("equal")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "pie_modules_replica")
