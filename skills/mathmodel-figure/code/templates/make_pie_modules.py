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
from plot_style import COLOR_INK, COLOR_ROCK, save_fig

PIE_COLORS = ["#7F99C5", "#D38083", "#B7CAE4", "#E5BFC0"]   # 低饱和发散族：柔蓝/柔红/淡蓝/淡红


def make_figure(output_stem: Path) -> None:
    """模块占比饼图：≤5 类、扁平无立体、细灰分割线、百分比内嵌。模拟数据：管线耗时构成。"""
    labels = ["特征提取", "模型推理", "数据加载", "其他"]
    sizes = [52, 30, 12, 6]

    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    wedges, _, autotexts = ax.pie(
        sizes, autopct="%1.1f%%", colors=PIE_COLORS, startangle=90,
        counterclock=False, wedgeprops=dict(edgecolor=COLOR_ROCK, linewidth=0.8),
        textprops={"fontsize": 9})
    for t in autotexts:
        t.set_fontsize(8)
        t.set_color(COLOR_INK)
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1.0, 0.5),
              frameon=False, fontsize=9)
    ax.set_title("求解管线各模块耗时占比", pad=12)
    ax.set_aspect("equal")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "pie_modules_replica")
