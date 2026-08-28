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
from plot_style import (ACCENT_ORANGE, COLOR_BASELINE, COLOR_MAIN, FIG_TALL, FS_ANNOT,
                        NEUTRAL_MID, save_fig, style_axes)


def pareto_mask(objs: np.ndarray) -> np.ndarray:
    """非支配（Pareto 前沿）判定掩膜：min-min 双目标。"""
    n = objs.shape[0]
    dom = np.zeros(n, dtype=bool)
    for i in range(n):
        better = np.all(objs <= objs[i], axis=1) & np.any(objs < objs[i], axis=1)
        if better.any():
            dom[i] = True
    return ~dom


def knee_point(front: np.ndarray) -> np.ndarray:
    """拐点解：前沿上到两端连线上距离最大的点（折衷解的经验判据）。"""
    p0, p1 = front[0], front[-1]
    dx, dy = p1 - p0
    span = np.hypot(dx, dy)
    if span == 0:
        return front[len(front) // 2]
    dist = np.abs(dx * (front[:, 1] - p0[1]) - dy * (front[:, 0] - p0[0])) / span
    return front[int(np.argmax(dist))]


def make_figure(output_stem: Path) -> None:
    """Pareto 前沿图：候选解作浅灰点云、非支配前沿为主角蓝线（白心标记）。

    拐点解用强调橙星标、理想点用灰虚线投影到两轴，说明前沿的几何含义。模拟数据：双目标解集。
    """
    rng = np.random.default_rng(11)
    t = rng.uniform(0, 1, 260)
    f1 = 4.2 * (1 - t) ** 1.6 + 0.9 * t + rng.normal(0, 0.28, 260) + 0.6
    f2 = 3.4 * t ** 1.4 + 0.7 * (1 - t) + rng.normal(0, 0.22, 260) + 0.5
    objs = np.column_stack([f1, f2])
    front = objs[pareto_mask(objs)]
    front = front[np.argsort(front[:, 0])]
    knee = knee_point(front)
    ideal = np.array([objs[:, 0].min(), objs[:, 1].min()])

    fig, ax = plt.subplots(figsize=FIG_TALL)
    ax.scatter(objs[:, 0], objs[:, 1], s=14, c=NEUTRAL_MID, alpha=0.45,
               edgecolors="none", label="候选解", zorder=2)
    ax.plot(front[:, 0], front[:, 1], color=COLOR_MAIN, linewidth=2.0, marker="o",
            markersize=5.5, markerfacecolor="white", markeredgecolor=COLOR_MAIN,
            markeredgewidth=1.2, label="Pareto 前沿（非支配解）", zorder=4)
    ax.scatter(*knee, marker="*", s=190, c=ACCENT_ORANGE, edgecolors="white",
               linewidths=0.8, zorder=6, label="拐点（折衷解）")
    ax.annotate(f"拐点  f=({knee[0]:.2f}, {knee[1]:.2f})", knee,
                xytext=(-10, -30), textcoords="offset points", fontsize=FS_ANNOT,
                color=ACCENT_ORANGE, ha="right",
                arrowprops=dict(arrowstyle="-", color=ACCENT_ORANGE, linewidth=0.8))
    ax.scatter(*ideal, marker="D", s=48, facecolor="none", edgecolors=COLOR_BASELINE,
               linewidths=1.2, zorder=6, label="理想点（不可达）")
    x_lo, y_lo = objs[:, 0].min() - 0.5, objs[:, 1].min() - 0.5
    ax.set_xlim(x_lo, objs[:, 0].max() + 0.5)
    ax.set_ylim(y_lo, objs[:, 1].max() + 0.5)
    ax.plot([ideal[0], ideal[0]], [y_lo, ideal[1]], linestyle=(0, (2, 2)),
            linewidth=0.8, color=COLOR_BASELINE, zorder=1)
    ax.plot([x_lo, ideal[0]], [ideal[1], ideal[1]], linestyle=(0, (2, 2)),
            linewidth=0.8, color=COLOR_BASELINE, zorder=1)
    ax.set_xlabel("目标 f1（成本）")
    ax.set_ylabel("目标 f2（风险）")
    style_axes(ax, grid="both")
    ax.legend(loc="upper right", frameon=True, facecolor="white",
              framealpha=0.85, edgecolor="none")   # 点云密集处需半透明白底托住图例
    ax.set_title("双目标优化非支配解集")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "pareto_front_replica")
