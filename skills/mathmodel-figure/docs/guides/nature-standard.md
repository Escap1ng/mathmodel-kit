# Nature 出图标准（模板库外现绘用）

本文件是**现绘参照**：当 `code/templates/` 的 20 个模板不能准确表达数据或结论时，
按本标准从零起图。图型按**数据形态与要论证的结论**选择，模板库只是加速器，不是边界——
**禁止为套用模板而改数据语义、禁止把不相干的图硬凑成多子图**。

分工：色值、字号、线型等**数值条文**以 [visualization-rules.md](visualization-rules.md) 为唯一权威出处；
本文件只给**起图流程、最小骨架、图型选择表与跨图统一契约**。

## 六条硬标准（每张现绘图都必须同时满足）

1. **样式来源唯一**：`from plot_style import ...`，尺寸取 `FIG_*`、字号取 `FS_*`、颜色取语义常量；
   脚本内不写十六进制色值、不写裸字号。
2. **坐标框架**：调 `style_axes(ax, grid='y')`（横向条形 `grid='x'`，散点可 `grid='both'`，
   热图例外需四边闭合）；数值轴按规范从 0 起，不得误导性截断。
3. **颜色只承担三种职责**：身份（`identity_color(i)`，第 0 号恒为主角蓝）、
   方向（`delta_annotation()` 的 `↑/↓` 红绿，只用于有正负的增量）、
   层级（`TONE_RAMP` / `tint()`，深=主证据、浅=陪衬）；基准与均值线一律 `COLOR_BASELINE`。
4. **文字最少且可读**：Arial 无衬线栈由 `plot_style` 统一设定；轴标签带物理量与单位；
   **禁止 mathtext 与中文混排**（`"问题规模 $n$（个）"` 会让中文变方框）；
   系列 ≤5 条时优先线尾/条端**直接标注**取代图例。
5. **证据完整**：不确定度、样本量、对照基准该显示就显示（置信带 `FILL_ALPHA`、
   误差棒、`R²`/RMSE/n 文字框）；显示每一次观测，别只画均值。
6. **渲染自检**：出图后打开 PNG 逐项核对
   [visualization-rules.md 的渲染自检清单](visualization-rules.md)，
   代码跑通不等于图没问题；不过就改脚本重渲染。

## 最小起图骨架

复制到工作区 `scripts/make_custom_<主题>.py` 后改写数据与图型，其余保持不动：

```python
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
from plot_style import (COLOR_BASELINE, COLOR_MAIN, FIG_FULL, FS_ANNOT, FILL_ALPHA,
                        save_fig, style_axes)


def make_figure(output_stem: Path) -> None:
    """一句话说明这张图要证明什么。模拟数据：<来源与构造方式>。"""
    rng = np.random.default_rng(2026)          # 种子固定，保证可复现
    x = np.linspace(0, 10, 60)
    y_main = np.sin(x) + rng.normal(0, 0.12, x.size)
    y_base = 0.6 * np.cos(x)

    fig, ax = plt.subplots(figsize=FIG_FULL)   # 尺寸取自 plot_style，勿手写
    ax.fill_between(x, y_main - 0.15, y_main + 0.15, color=COLOR_MAIN, alpha=FILL_ALPHA,
                    label="±1σ 区间", zorder=2)
    ax.plot(x, y_main, color=COLOR_MAIN, linewidth=2.2, label="本文方法", zorder=4)
    ax.plot(x, y_base, color=COLOR_BASELINE, linewidth=1.4, linestyle="--",
            label="基准", zorder=3)
    ax.text(x[-1], y_main[-1], " 本文方法", color=COLOR_MAIN, fontsize=FS_ANNOT, va="center")
    ax.set_xlabel("自变量 x")                  # 图内文字禁 mathtext 混排中文
    ax.set_ylabel("目标值 y")
    ax.set_ylim(0, None)                       # 性能类数值轴从 0 起
    style_axes(ax, grid="y")
    ax.legend(loc="lower left")
    ax.set_title("图题写结论，不写绘制过程")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(output_stem.with_suffix(".png")), close=False)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_figure(ROOT / "outputs" / "custom_example_replica")
```

多子图版式（主次分明，面板标号必给；需再 import `FIG_TALL` 与 `add_panel_label`）：

```python
fig = plt.figure(figsize=FIG_TALL)
gs = fig.add_gridspec(2, 2, width_ratios=[1.5, 1], height_ratios=[1, 1],
                      hspace=0.45, wspace=0.3)
ax_hero = fig.add_subplot(gs[:, 0])            # 主证据占大版面
ax_b, ax_c = fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])
for ax, tag in ((ax_hero, "a"), (ax_b, "b"), (ax_c, "c")):
    style_axes(ax, grid="y")
    add_panel_label(ax, tag)                   # 与 fit-conf-residual 同款
```

## 模板库外图型选择表

| 数据形态 / 要论证的结论 | 建议图型 | 现绘要点（复用 `plot_style`） |
| --- | --- | --- |
| 参数空间的最优盆地、温度场 | 等高线 + 填充 | `contourf` 配 `SEQUENTIAL_CMAP`，色条 label 带单位，`style_axes(ax, grid=None)` 免与曲线打架 |
| 两个状态量互相演化 | 相图 / 零净增长线 | 两条轨迹取主角蓝与橙实线，零线 `COLOR_BASELINE` 虚线，方向箭头用细 `quiver` |
| 构成随时间变化 | 堆叠面积图 | 各层取 `TONE_RAMP` 或身份色序列 + 白 0.6pt 分隔；总量另轴虚线 |
| 多指标综合评价 | 雷达图 | 填充主角蓝 α0.2、轮廓 2pt，对比模型取次系列虚线 α0.1，网格 `NEUTRAL_LIGHT` |
| 工序/排期 | 甘特图 | `barh` + `TONE_RAMP`，关键里程碑用 `ACCENT_ORANGE` 星标 |
| 单因素敏感性排序 | 龙卷风图 | 以 `COLOR_BASELINE_DARK` 虚线为中轴，正负偏离用方向色（此处确为有向变化） |
| 权重扰动的升降幅度 | 差值双柱 | 差值标注统一用 `delta_annotation()`，保留 `↑/↓` 过灰度 |
| 高维样本结构、聚类效果 | 平行坐标 | 每类 ≤60 条、α0.3–0.5，按类取 `identity_color(i)`，图例置图外 |
| 流量/转移/耦合结构 | 桑基图 | 节点取身份色，连线继承起点色 α0.5（关系结构优先试 `nature-chord-diagram`） |
| 分区域指标 | 地图热力图 | 底图浅灰极简，数据层 `SEQUENTIAL_CMAP`，**禁红绿** |
| 单序列分布形态 | 直方图 + KDE | 柱主角蓝 α0.6、KDE 主线 2pt、均值灰虚线 |
| 两组分布差异 | 小提琴 + 箱线 | 优先复用 `paired-raincloud`；自绘时 KDE 填 α0.15 |
| 预测 vs 真值 | 散点 + 45° 线 | 点主角蓝 α0.6、45° 线 `COLOR_BASELINE` 虚线、`R²`/RMSE 文字框 |
| 多方法 × 多指标 | 小多图 small multiples | `subplots(..., sharey=True)` + `add_panel_label()`，同指标共享上下限 |
| 同主题双量纲 | 双轴图 | 左轴主角蓝、右轴橙，两套线型，两个 y 轴标题各带单位 |
| 优化解集与前沿 | 点云 + 前沿线 | 参照 `pareto-front`：候选解浅灰、前沿主角蓝白心标记 |

## 跨图风格统一契约（全文所有图强制）

- **先登记再画图**：动笔前定一张方法-颜色对照（本文=主角蓝、对照方法=橙/紫/青、
  基准=灰、种群/背景=浅调），全文每张图（含模板图与现绘图）都按这张表取色；
- **模板图与现绘图混排时**，两者共用 `plot_style.py` 同一套常量，视觉差只允许来自图型本身；
- **字号与尺寸一致**：现绘图用 `FIG_FULL`/`FIG_TALL`/`FIG_SQUARE` 与 `FS_*`，
  不出现"这张图字大一点"的临时调整；缩放展示按规范提 `font_scale`；
- **色相超 6 个**说明图型选错了，改分图或热图，而不是继续加色；
- **图题口径一致**：一句话写结论，不写绘制过程；图题在图下方由论文排版给出，图内标题保持简短。

## 何时把现绘图反哺进模板库

同一图型在论文里出现 ≥2 次、或属于竞赛高频图型时，按
[README 的扩展约定](../../README.md) 登记为正式模板：`code/templates/make_<id>.py`
（自带确定性模拟数据、三格式导出）+ `docs/templates/figure-catalog.md` 加行
+ `examples/previews/<id>_replica.png` + `code/tools/render_template.py` 注册 id + `SKILL.md` 清单加行。
