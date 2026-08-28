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
from plot_style import (COLOR_BASELINE, COLOR_BASELINE_DARK, FILL_ALPHA, FIG_TALL, FS_ANNOT,
                        FS_TICK, NEUTRAL_BG, COLOR_MAIN, add_panel_label, save_fig, style_axes)


def make_figure(output_stem: Path) -> None:
    """拟合对比图（a 拟合曲线 + 95% 置信带、b 残差）：观测值为中性灰、模型为主角蓝。

    面板用粗体 a/b 标号，拟合优度以文字标注直接给出。模拟数据：对数响应 + 高斯噪声。
    """
    rng = np.random.default_rng(7)
    x = np.linspace(0.5, 9.5, 46)
    y = 2.4 * np.log(x) + 0.35 * x + rng.normal(0, 0.55, x.size)

    coef = np.polyfit(x, y, 2)
    xs = np.linspace(x.min(), x.max(), 200)
    fit = np.polyval(coef, xs)
    pred = np.polyval(coef, x)
    resid = y - pred
    sigma = resid.std(ddof=3)
    se = 1.96 * sigma * np.sqrt(1 / x.size + (xs - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum())
    r2 = 1 - (resid ** 2).sum() / ((y - y.mean()) ** 2).sum()
    rmse = float(np.sqrt((resid ** 2).mean()))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIG_TALL, sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1], "hspace": 0.12})
    ax1.scatter(x, y, s=22, c=COLOR_BASELINE, alpha=0.55, edgecolors="white",
                linewidth=0.5, label="观测值", zorder=3)
    ax1.plot(xs, fit, color=COLOR_MAIN, linewidth=2.2, label="二次拟合曲线", zorder=4)
    ax1.fill_between(xs, fit - se, fit + se, color=COLOR_MAIN, alpha=FILL_ALPHA,
                     label="95% 置信带", zorder=2)
    ax1.text(0.025, 0.955, f"R² = {r2:.3f}\nRMSE = {rmse:.3f}\nn = {x.size}",
             transform=ax1.transAxes, fontsize=FS_ANNOT, va="top", ha="left",
             color=COLOR_BASELINE_DARK,
             bbox=dict(boxstyle="round,pad=0.4", facecolor=NEUTRAL_BG, edgecolor="none"))
    ax1.set_ylabel("响应值 y")
    ax1.legend(loc="lower right", ncols=3)
    style_axes(ax1, grid="y")
    add_panel_label(ax1, "a")

    ax2.scatter(x, resid, s=16, c=COLOR_MAIN, alpha=0.75, edgecolors="white", linewidth=0.3,
                zorder=3)
    ax2.axhline(0, color=COLOR_BASELINE_DARK, linewidth=1.0, linestyle="--", zorder=2)
    ax2.fill_between([x.min(), x.max()], -2 * sigma, 2 * sigma, color=COLOR_BASELINE,
                     alpha=0.08, zorder=1)
    ax2.text(0.015, 2 * sigma, "±2σ 残差带", transform=ax2.get_yaxis_transform(),
             fontsize=FS_ANNOT, color=COLOR_BASELINE, va="center", ha="left")
    ax2.set_xlabel("自变量 x")
    ax2.set_ylabel("残差")
    ax2.tick_params(axis="x", labelsize=FS_TICK)
    style_axes(ax2, grid="y")
    add_panel_label(ax2, "b")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "fit_confidence_residual_replica")
