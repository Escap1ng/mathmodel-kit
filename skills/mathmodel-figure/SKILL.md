---
name: mathmodel-figure
description: 数学建模/科研数据图表模板技能：20 个开箱即用的 Python/matplotlib 模板（相关热图、拟合置信带+残差、迭代收敛、Pareto前沿、性能折线对比、分组柱状、箱线+抖动、模块占比饼图、长类别条形、SHAP组合、配对云雨、交叉验证ROC、泰勒图、相关矩阵pairgrid、预测-真实边缘分布、TPE调参三维曲面、半边小提琴、分组环形热图、城市公园降温组合、Nature和弦图）。当用户要画/复刻上述任意图表、问"科研绘图模板"、需要论文结果图或数模竞赛配图时使用。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 数学建模数据图表模板（mathmodel-figure）

内置 20 个可直接运行的 Python/matplotlib 模板：自带**确定性模拟数据**，一条命令产出
PNG/PDF/SVG 三格式出版级图表。适合数模竞赛论文配图与科研结果图。

## 快速路径

1. 在 `docs/templates/figure-catalog.md` 里匹配用户要的图（id ↔ 中文图题）。
2. 在工作目录运行渲染器，传模板 id（支持 id / 英文别名 / 中文图题片段）：

```bash
python3 code/tools/render_template.py paired-raincloud
```

3. 渲染器把模板脚本（及其依赖的 `plot_style.py` 样式模块）复制到 `绘图复刻/scripts/`，
   并在该目录运行，产物写入 `绘图复刻/outputs/`。
4. 把生成的 PNG/PDF/SVG 路径与复制出的脚本路径返回给用户。

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

**基础与高频类**（统一走 `code/style/plot_style.py` 学术色板）：
`heatmap-annotated`、`fit-conf-residual`、`convergence-curve`、`pareto-front`、
`line-compare`、`grouped-bar`、`boxplot-jitter`、`pie-modules`、`hbar-longlabel`

## 定制与规范

用户要求改动时，先复制并运行最接近的模板，再编辑 `绘图复刻/scripts/` 里的副本。必须保留：

- 在 import matplotlib 之前设置 `MPLCONFIGDIR`；
- 模拟数据的确定性随机种子；
- PNG/PDF/SVG 三格式导出；
- 可读的标签、图例与高 DPI 输出。

配色、字号、线型、图例、黑白打印等**出图规范**见 `docs/guides/visualization-rules.md`
（统一样式模块 `code/style/plot_style.py` 是其代码化实现）；
实现配方见 `docs/guides/plot-recipes.md`。
