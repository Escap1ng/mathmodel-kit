# mathmodel-figure

数学建模/科研数据图表绘制技能（21 个 matplotlib 模板）。入口文件是 [SKILL.md](SKILL.md)，本 README 只说明目录组织，与 `mathmodel-diagram` 采用同一套分类规范。

## 目录结构

```
mathmodel-figure/
├── SKILL.md                # 技能入口：匹配模板 → 调渲染器 → 返回产物路径
├── README.md               # 本文件：结构说明
├── code/                   # 全部 Python 源码
│   ├── style/
│   │   └── plot_style.py   #   统一样式模块（学术低饱和色板/字体回退/save_fig，规范条文化见 docs）
│   ├── templates/          #   21 个图模板（自带确定性模拟数据，可直接运行）
│   │   └── make_<template>.py
│   └── tools/              #   通用工具
│       └── render_template.py   # 渲染器：解析 id/别名/中文提示 → 复制模板(+样式)到工作区 → 运行并收集产物
├── docs/                   # 全部 Markdown 文档
│   ├── templates/
│   │   └── figure-catalog.md    # 模板目录：id ↔ 脚本 ↔ 图题 对照表
│   └── guides/
│       ├── visualization-rules.md  # 出图可视化规范（配色/图型/强制要求，唯一权威出处）
│       └── plot-recipes.md         # 模板定制实现配方
└── examples/
    └── previews/           # 21 张模板效果预览（<template>_replica.png），与 code/templates/ 同名对齐
```

## 分类依据

- **一级按内容类型分**（`code/` `docs/` `examples/`）：与 `mathmodel-diagram` 保持一致的顶层目录词表。
- **二级按功能模块分**：`code/templates`（模板本体）↔ `docs/templates/figure-catalog.md`（模板索引）↔ `examples/previews`（模板效果）以模板 id 三方对齐；样式收敛于 `code/style/plot_style.py`；渲染器属与模板无关的通用工具，放 `code/tools`。
- **层级最深 3 层**（`code/style/`），新增模板只需在对应目录加同名条目。

## 两套模板家族

- **高端组合类**（11 个，自带配色体系）：SHAP、云雨、ROC、Taylor、pairgrid、边缘分布、TPE 曲面、半边小提琴、环形热图、城市降温、和弦；
- **基础与高频类**（10 个，统一 `from plot_style import`）：三维曲面、相关热图、拟合+残差、收敛、Pareto、折线、分组柱状、箱线+抖动、饼、条形。

## 扩展约定

新增图模板的交付清单：

```
code/templates/make_<template_id>.py        # 自带确定性模拟数据，输出 PNG/PDF/SVG 三格式
docs/templates/figure-catalog.md            # 目录表加一行（id / script / 图题）
examples/previews/<template_id>_replica.png # 1:1 效果预览（运行模板生成）
code/tools/render_template.py               # SCRIPT_MAP（及可选 ALIASES / CJK_HINTS）注册 id
SKILL.md                                    # 模板清单加一行
```

模板脚本约定：文件头设 `MPLCONFIGDIR`（先于 import matplotlib）、确定性随机种子、
`ROOT / "outputs"` 默认输出路径——渲染器复制到工作区后依赖该相对结构；
依赖样式模块的模板写 `from plot_style import ...`，渲染器会自动把 `code/style/plot_style.py`
一并复制进工作区 `scripts/`。
