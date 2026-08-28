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
from plot_style import (COLOR_BASELINE, COLOR_MAIN, COLOR_MAIN_PALE, FIG_FULL, FS_ANNOT,
                        delta_annotation, save_fig, style_axes)


def make_figure(output_stem: Path) -> None:
    """迭代收敛曲线：种群散点作浅色背景、最优适应度为主角线、均值线恒为中灰基准。

    最优–均值之间填浅色区间，并标出收敛代数与累计提升（有向变化才用方向色）。
    模拟数据：遗传算法最大化适应度，150 代求解过程。
    """
    rng = np.random.default_rng(2024)
    gens = np.arange(1, 151)
    pop = 120
    best = 1.6 + 8.2 * (1 - np.exp(-gens / 28)) + rng.normal(0, 0.02, gens.size)
    mean = best - (1.9 * np.exp(-gens / 40) + 0.22)
    all_fit = np.stack([np.maximum(best[g] - np.abs(rng.normal(0, 0.9 * np.exp(-g / 55) + 0.35, pop)), 0.0)
                        for g in range(gens.size)])
    gen_grid = np.repeat(gens[:, None], pop, axis=1)
    # 收敛判据：连续 10 代相对改善 < 1%
    rel = np.array([(best[g] - best[g - 10]) / best[g - 10] for g in range(10, gens.size)])
    hit = np.flatnonzero(rel < 1e-2)
    conv = int(gens[10:][hit[0]]) if hit.size else int(gens[-1])
    gain, gain_color = delta_annotation(best[0], best[-1])

    fig, ax = plt.subplots(figsize=FIG_FULL)
    ax.scatter(gen_grid[::2, ::2], all_fit[::2, ::2], s=5, c=COLOR_MAIN_PALE, alpha=0.6,
               label="种群个体", rasterized=True, edgecolors="none", zorder=2)
    ax.fill_between(gens, best, mean, color=COLOR_MAIN, alpha=0.08,
                    label="最优–均值区间", zorder=3)
    ax.plot(gens, mean, color=COLOR_BASELINE, linewidth=1.4, linestyle="--",
            label="均值适应度", zorder=4)
    ax.plot(gens, best, color=COLOR_MAIN, linewidth=2.2, label="最优适应度", zorder=5)
    ax.axvline(conv, color=COLOR_BASELINE, linewidth=0.9, linestyle=(0, (3, 3)), zorder=4)
    ax.text(conv - 2, 0.55, f"≈第 {conv} 代收敛", transform=ax.get_xaxis_transform(),
            fontsize=FS_ANNOT, color=COLOR_BASELINE, ha="right", va="center")
    ax.text(0.02, 0.96, f"最优适应度 {best[0]:.2f} → {best[-1]:.2f}（{gain}）",
            transform=ax.transAxes, fontsize=FS_ANNOT, color=gain_color, ha="left", va="top")
    ax.set_xlabel("迭代代数")
    ax.set_ylabel("适应度值")
    ax.set_xlim(1, gens[-1])
    ax.set_ylim(0, np.nanmax(all_fit) * 1.06)
    style_axes(ax, grid="y")
    ax.legend(loc="lower right", ncols=2)
    ax.set_title("遗传算法收敛过程")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "convergence_curve_replica")
