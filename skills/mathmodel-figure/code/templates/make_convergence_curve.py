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
from plot_style import COLOR_ACCENT, COLOR_MAIN, COLOR_SAGE, save_fig


def make_figure(output_stem: Path) -> None:
    """迭代收敛曲线：种群散点背景 + 最优/均值适应度主线。模拟数据：GA 求解过程。"""
    rng = np.random.default_rng(2024)
    gens = np.arange(1, 151)
    pop = 120
    best = 9.8 - 8.2 * (1 - np.exp(-gens / 28)) + rng.normal(0, 0.02, gens.size)
    mean = best + 1.9 * np.exp(-gens / 40) + 0.22
    all_fit = np.stack([np.maximum(best[g] + rng.normal(0, 0.9 * np.exp(-g / 55) + 0.35, pop), best[g])
                        for g in range(gens.size)])
    gen_grid = np.repeat(gens[:, None], pop, axis=1)

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.scatter(gen_grid[::2, ::2], all_fit[::2, ::2], s=5, c=COLOR_MAIN, alpha=0.15,
               label="种群个体", rasterized=True, edgecolors="none")
    ax.plot(gens, best, color=COLOR_ACCENT, linewidth=2.5, label="最优适应度", zorder=5)
    ax.plot(gens, mean, color=COLOR_SAGE, linewidth=1.5, linestyle="--",
            label="均值适应度", alpha=0.85)
    ax.set_xlabel("迭代代数", fontsize=11)
    ax.set_ylabel("适应度值", fontsize=11)
    ax.set_xlim(1, gens[-1])
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3, linestyle=":", linewidth=0.8)
    ax.set_title("遗传算法收敛过程", pad=12)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "convergence_curve_replica")
