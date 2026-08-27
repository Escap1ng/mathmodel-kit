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
from plot_style import SURFACE_CMAP, save_fig


def make_figure(output_stem: Path) -> None:
    """三维曲面图（带底部投影，单色渐变"石膏雕塑感"）。模拟数据：双参数目标函数。"""
    a = np.linspace(-3, 3, 120)
    b = np.linspace(-3, 3, 120)
    A, B = np.meshgrid(a, b)
    Z = (A - 1.2) ** 2 * np.exp(-A ** 2 - B ** 2) * 6 + 0.6 * B ** 2 * np.exp(-A ** 2) + 1.5

    fig = plt.figure(figsize=(7.2, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(A, B, Z, cmap=SURFACE_CMAP, alpha=0.95, edgecolor="none",
                    antialiased=True, rstride=2, cstride=2)
    ax.contourf(A, B, Z, zdir="z", offset=Z.min(), cmap=SURFACE_CMAP, alpha=0.5)
    fig.colorbar(ax.collections[0], ax=ax, shrink=0.55, pad=0.12, label="目标函数值")
    ax.set_xlabel("参数 $\\alpha$", labelpad=12)
    ax.set_ylabel("参数 $\\beta$", labelpad=12)
    ax.zaxis.set_rotate_label(False)
    ax.set_zlabel("目标值", labelpad=8)
    ax.view_init(elev=25, azim=135)
    ax.set_title("双参数目标函数曲面与最优区域", pad=16)

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "surface_3d_replica")
