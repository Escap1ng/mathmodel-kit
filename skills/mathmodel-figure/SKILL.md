---
name: mathmodel-figure
description: 数学建模/科研数据图表技能：20 个开箱即用的 Python/matplotlib 模板，简单图型统一采用 Nature 风格（身份/方向/层级三色职责、Arial 小字、细轴线、直接标注）；模板不匹配时按 docs/guides/nature-standard.md 的 Nature 出图标准现绘，共用同一套样式模块。覆盖相关热图、拟合置信带+残差、迭代收敛、Pareto前沿、性能折线对比、分组柱状、箱线+抖动、模块占比环形图（饼图）、长类别条形、SHAP组合、配对云雨、交叉验证ROC、泰勒图、相关矩阵pairgrid、预测-真实边缘分布、TPE调参三维曲面、半边小提琴、分组环形热图、城市公园降温组合、Nature和弦图。当用户要画/复刻上述任意图表、问"科研绘图模板/Nature 风格出图"、需要论文结果图或数模竞赛配图时使用。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 数学建模数据图表模板（mathmodel-figure）

内置 20 个可直接运行的 Python/matplotlib 模板：自带**确定性模拟数据**，一条命令产出
PNG/PDF/SVG 三格式出版级图表。简单图型走 `code/style/plot_style.py` 的 Nature 样式系统
（小字无衬线、细轴线、颜色只承担语义）。适合数模竞赛论文配图与科研结果图。

## 快速路径

1. 在 `docs/templates/figure-catalog.md` 里匹配用户要的图（id ↔ 中文图题）。
   **匹配不到就走「模板库之外」现绘**（见下文），不要硬套最接近的模板、更不要为套模板改数据语义。
2. 在工作目录运行渲染器，传模板 id（支持 id / 英文别名 / 中文图题片段）：

```bash
python3 code/tools/render_template.py paired-raincloud
```

3. 渲染器把模板脚本（及其依赖的 `plot_style.py` 样式模块）复制到 `绘图复刻/scripts/`，
   并在该目录运行，产物写入 `绘图复刻/outputs/`。
4. 打开生成的 PNG 做**渲染自检**（清单见 `docs/guides/visualization-rules.md` 末节）：
   查裁切、压线、空子图、灰度可辨、颜色语义；不过就改工作区脚本重跑。
5. 把生成的 PNG/PDF/SVG 路径与复制出的脚本路径返回给用户。

用 `--list` 查看全部支持的 id：

```bash
python3 code/tools/render_template.py --list
```

## 输出契约

- 默认项目目录：`绘图复刻`（`--project` 可改）。
- 脚本路径：`绘图复刻/scripts/make_<template>.py`。
- 产物：`绘图复刻/outputs/<template>_replica.png`、`.pdf`、`.svg`（PNG 默认 300 DPI，密度类图可降至 200，见 visualization-rules.md）。
- 优先用内置模板；用户要定制时，改**工作区里复制出的脚本**，不动技能内置模板。
- 内置模板用确定性模拟数据。不得声称模拟数据复现了某篇文献的真实结果。

## 模板清单

**高端组合类**（自带配色体系）：`multiclass-shap-combo`、`paired-raincloud`、`cv-roc-ci`、
`taylor-diagram`、`correlation-pairgrid`、`prediction-marginal-grid`、`rf-tpe-surface`、
`grouped-corr-split-violin`、`grouped-circular-heatmap`、`urban-park-cooling-combo`、
`nature-chord-diagram`

**基础与高频类**（9 个，统一走 `code/style/plot_style.py` 的 Nature 样式系统）：
`heatmap-annotated`、`fit-conf-residual`、`convergence-curve`、`pareto-front`、
`line-compare`、`grouped-bar`、`boxplot-jitter`、`pie-modules`、`hbar-longlabel`

## 模板库之外（Nature 标准现绘）

模板库不是边界：**图型由数据结构与要论证的结论决定**。20 个模板覆盖不了时
（等高线、相图、堆叠面积、雷达、甘特、龙卷风、平行坐标、桑基、地图热力、小多图、双轴图等），
按 `docs/guides/nature-standard.md` 现绘——那里给出六条硬标准、可直接运行的最小起图骨架、
多子图版式片段、模板库外图型选择表，以及跨图风格统一契约。

现绘图与模板图共用 `code/style/plot_style.py`：同一方法在两类图里必须同色，
尺寸/字号/线型/坐标框架一律取自该模块，保证全文风格统一。同一图型反复出现（≥2 次）
或属竞赛高频图型时，按 README 的扩展约定把它登记为正式模板。

## 定制与规范

用户要求改动时，先复制并运行最接近的模板，再编辑 `绘图复刻/scripts/` 里的副本。必须保留：

- 在 import matplotlib 之前设置 `MPLCONFIGDIR`；
- 模拟数据的确定性随机种子；
- PNG/PDF/SVG 三格式导出；
- 可读的标签、图例与高 DPI 输出；
- `style_axes(ax, grid='y')` 坐标框架与 `save_fig` 导出入口，改样式请改 `plot_style.py`。

定制时用 `plot_style` 的语义常量与助手，不要在脚本里写十六进制色值或裸字号：
`identity_color(i)`（次系列身份色）、`TONE_RAMP`（明度层级）、`tint()`（同族降饱和）、
`delta_annotation()`（有向变化 → `↑/↓` + 红绿）、`annotate_bars()`（柱端数值）、
`add_panel_label()`（多子图 a/b 标号）。图内文字禁止 mathtext 与中文混排（中文会变方框）。

配色、字号、线型、图例、版式、黑白打印与渲染自检等**出图规范**见
`docs/guides/visualization-rules.md`（统一样式模块 `code/style/plot_style.py` 是其代码化实现）；
实现配方见 `docs/guides/plot-recipes.md`。
