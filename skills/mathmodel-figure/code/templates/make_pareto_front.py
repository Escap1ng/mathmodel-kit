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
from plot_style import COLOR_ACCENT, COLOR_INK, COLOR_ROCK, save_fig


def pareto_mask(objs: np.ndarray) -> np.ndarray:
    """非支配（Pareto 前沿）判定掩膜：min-min 双目标。"""
    n = objs.shape[0]
    dom = np.zeros(n, dtype=bool)
    for i in range(n):
        better = np.all(objs <= objs[i], axis=1) & np.any(objs < objs[i], axis=1)
        if better.any():
            dom[i] = True
    return ~dom


def make_figure(output_stem: Path) -> None:
    """Pareto 前沿图：全部候选解灰底散点 + 非支配前沿白心标记连线。模拟数据：双目标解集。"""
    rng = np.random.default_rng(11)
    t = rng.uniform(0, 1, 260)
    f1 = 4.2 * (1 - t) ** 1.6 + 0.9 * t + rng.normal(0, 0.28, 260) + 0.6
    f2 = 3.4 * t ** 1.4 + 0.7 * (1 - t) + rng.normal(0, 0.22, 260) + 0.5
    objs = np.column_stack([f1, f2])
    front = objs[pareto_mask(objs)]
    order = np.argsort(front[:, 0])
    front = front[order]

    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.scatter(objs[:, 0], objs[:, 1], s=16, c=COLOR_ROCK, alpha=0.35,
               edgecolors="none", label="候选解", zorder=2)
    ax.plot(front[:, 0], front[:, 1], color=COLOR_ACCENT, linewidth=2, marker="o",
            markersize=6, markerfacecolor="white", markeredgecolor=COLOR_ACCENT,
            markeredgewidth=1.5, label="Pareto 前沿", zorder=4)
    ax.set_xlabel("目标 $f_1$（成本）", fontsize=11)
    ax.set_ylabel("目标 $f_2$（风险）", fontsize=11)
    ax.legend(frameon=True, fancybox=True, framealpha=0.8, loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.25, linestyle=":", linewidth=0.8)
    ax.set_title("双目标优化非支配解集", pad=12, color=COLOR_INK)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "pareto_front_replica")
