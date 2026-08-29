<h1 align="center">mathmodel-kit</h1>

<p align="center">
  数学建模竞赛一站式 Agent 技能集<br>
  赛题分析 · 模型构建 · 算法实现 · 出版级图表 · 论文成稿与评分
</p>

<p align="center">
  <a href="https://github.com/Escap1ng/mathmodel-kit/actions/workflows/ci.yml"><img src="https://github.com/Escap1ng/mathmodel-kit/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Escap1ng/mathmodel-kit/actions/workflows/paper.yml"><img src="https://github.com/Escap1ng/mathmodel-kit/actions/workflows/paper.yml/badge.svg" alt="Paper LaTeX build"></a>
  <img src="https://img.shields.io/badge/%E8%AE%B8%E5%8F%AF%E8%AF%81-Apache--2.0-1A6FC4?style=flat" alt="许可证">
  <img src="https://img.shields.io/badge/Python-3-2E9E44?style=flat" alt="Python">
  <img src="https://img.shields.io/badge/%E6%8A%80%E8%83%BD-4-7B5FD6?style=flat" alt="技能数">
  <img src="https://img.shields.io/badge/%E6%A8%A1%E6%9D%BF-25-E28E2C?style=flat" alt="模板数">
  <img src="https://img.shields.io/badge/%E4%BA%A7%E7%89%A9-300DPI_%C2%B7_%E7%9F%A2%E9%87%8F-767676?style=flat" alt="产物规格">
</p>

<p align="center">
  <b>简体中文</b> &nbsp;·&nbsp; <a href="README_EN.md">English</a>
</p>

---

## 目录

[这是什么](#这是什么) · [技能矩阵](#技能矩阵) · [效果预览](#效果预览) · [设计取向](#设计取向) ·
[出图风格：Nature 标准](#出图风格nature-标准) · [工作流与质量门禁](#工作流与质量门禁) ·
[快速开始](#快速开始) · [仓库结构](#仓库结构) · [依赖与自测环境](#依赖与自测环境) ·
[常见问题](#常见问题) · [扩展与贡献](#扩展与贡献) · [致谢](#致谢) · [许可证](#许可证)

## 这是什么

`mathmodel-kit` 是一套面向数学建模竞赛的 agent 技能集，共四个技能，可单独使用，也可由主技能串成闭环：

- `math-modeling-helper`（主技能）：按「赛题分析 → 模型构建 → 算法实现 → 论文输出 → 评分优化」六个阶段编排全程，附带代码规范与评分口径；
- `mathmodel-figure`（数据图表）：内置 20 个 matplotlib 模板，模板不匹配时按 [`nature-standard.md`](skills/mathmodel-figure/docs/guides/nature-standard.md) 的规范现绘；
- `mathmodel-diagram`（学术示意图）：内置 5 个 JSON 驱动的版式模板，也支持从零手绘与照参考图高保真复刻；
- `mathmodel-paper`（论文输出）：提供 LaTeX 骨架，编译成 PDF 后转 Word，并按竞赛口径微调版式。

分工原则：**机械正确性交给技能，建模判断留给人**。数据可复现、图表不裁切不重叠、论文数字可追溯到脚本产物、格式过自检清单，这些由技能保证；方法选型、结果解释、创新点表述仍由使用者决定。

## 技能矩阵

| 技能 | 定位 | 入口 | 产物 |
|---|---|---|---|
| [`math-modeling-helper`](skills/math-modeling-helper/SKILL.md) | 主技能编排：赛题分析、算法选择、代码实现、论文写作与评分 | 提交赛题或建模需求即触发 | 工作目录骨架、代码与结果、论文与评分报告 |
| [`mathmodel-figure`](skills/mathmodel-figure/SKILL.md) | 数据图表：20 个 matplotlib 模板 + 模板库外的 Nature 出图标准 | `python3 code/tools/render_template.py <模板id>` | PNG(300 DPI) + PDF + SVG + 可改脚本 |
| [`mathmodel-diagram`](skills/mathmodel-diagram/SKILL.md) | 学术示意图：5 个 JSON 驱动模板，另支持手写与高保真复刻 | `python3 code/templates/<模板>.py content.json` | PNG(300 DPI) + 矢量 PDF + content JSON |
| [`mathmodel-paper`](skills/mathmodel-paper/SKILL.md) | 论文输出：LaTeX 骨架 → PDF → Word，含竞赛版式微调 | `xelatex` + `code/word_postprocess.py` | 合规 `.pdf` 与 `.docx`、摘要模板 |

## 效果预览

数据图表（`mathmodel-figure`）

| 分组柱状图（Nature 角色色板） | 配对云雨图 | Nature 风格和弦图 |
|---|---|---|
| <img src="skills/mathmodel-figure/examples/previews/grouped_bar_replica.png" width="330"> | <img src="skills/mathmodel-figure/examples/previews/paired_raincloud_replica.png" width="330"> | <img src="skills/mathmodel-figure/examples/previews/nature_chord_diagram_replica.png" width="330"> |

学术示意图（`mathmodel-diagram`）

| 五带技术路线图 | 问题分析流程图 | 三栏阶段流程图 |
|---|---|---|
| <img src="skills/mathmodel-diagram/examples/roadmap-5band/preview.png" width="240"> | <img src="skills/mathmodel-diagram/examples/problem-flow/preview.png" width="330"> | <img src="skills/mathmodel-diagram/examples/stageflow-3col/preview.png" width="330"> |

全部预览图与模板脚本 1:1 对应，改样式后重新渲染即可覆盖。

## 设计取向

- **全流程贯通** — 单一入口覆盖「赛题理解 → 模型构建 → 算法实现 → 论文输出 → 评分优化」，专项技能可独立调用。
- **出版级默认** — 图表 300 DPI、矢量优先；配色、字号、线型、坐标框架集中在一个样式模块里，改一处全局生效。
- **不依赖模板库** — 图型由数据结构与要论证的结论决定。模板是加速器，不是边界；模板不匹配时按标准现绘，风格仍然统一。
- **确定性与可复现** — 模板自带种子化模拟数据，示意图由 content JSON 驱动，任何产物都能重渲与二次修改。
- **机器化质量门禁** — 示意图字数超框即非零退出、渲染前逐槽量中文字宽、九区盘点与红队复审、论文自评分卡。
- **反造假约束** — 禁止编造文献与数据；模拟数据不得声称复现真实结果；论文数字须能追溯到脚本产物。

## 出图风格：Nature 标准

数据图表的简单图型统一采用 Nature 版式——小字无衬线、细轴线、去冗余图例，颜色分工遵循下表四条规则：

| 职责 | 取值 | 规则 |
|---|---|---|
| 身份 | 主角蓝 `#1A6FC4`，次系列橙/紫/青/珊红 | 同一方法在全文每张图里同色 |
| 基准 | 中灰 `#767676` | 对照、均值、参考线永远是灰 |
| 方向 | 绿 `#2E9E44` / 红 `#E53935` | 只标有正负的增量，并带 `↑/↓` 以过灰度打印 |
| 层级 | 同族明度阶梯（深 → 浅） | 主证据深、支持信息浅，不靠加色相区分主次 |

条文见 [`visualization-rules.md`](skills/mathmodel-figure/docs/guides/visualization-rules.md)，
模板库外现绘见 [`nature-standard.md`](skills/mathmodel-figure/docs/guides/nature-standard.md)
（六条硬标准 + 最小起图骨架 + 图型选择表 + 跨图统一契约）。两条路径共用同一套样式常量，
因此模板图与自绘图混排时看不出风格差。

## 工作流与质量门禁

```
阶段零 环境预检 ── xelatex / python-docx / 绘图库可用性检查
  ▼
阶段一 赛题分析与背景调研 ── 问题拆解、子问题定性
  ▼
阶段二 工作目录创建 ── code/ results/ figures/ paper/ 分目录落盘
  ▼
阶段三 算法选择 ── 候选比较与风险预判（内部推理，结论交给人）
  ▼
阶段四 代码实现 ── 可运行脚本 + 结果摘要 + 图表（≥300 DPI）
  ▼
阶段五 论文输出 ── LaTeX 成稿 → PDF → Word，图随文走
  ▼
阶段六 评分与优化 ── 自评分卡 + 一致性复核，未过不交付
```

## 快速开始

**1. 安装技能** — 把需要的技能目录复制到 agent 的技能目录（以 Claude Code 为例）：

```bash
cp -r skills/mathmodel-figure ~/.claude/skills/
```

在对话里直接说需求即可命中，例如：「用云雨图对比三组实验的耗时分布」「把这张参考图重画成技术路线图」。

**2. 数据图表**

```bash
cd skills/mathmodel-figure
python3 code/tools/render_template.py --list             # 查看全部 20 个模板 id
python3 code/tools/render_template.py paired-raincloud   # 支持 id / 英文别名 / 中文图题片段
python3 code/tools/render_template.py 模块占比环形图      # 中文图题也能匹配
```

产物落在 `绘图复刻/outputs/`（PNG/PDF/SVG），脚本落在 `绘图复刻/scripts/`，改样式改脚本不动内置模板。
模板不匹配时按 `docs/guides/nature-standard.md` 现绘，仍然 `from plot_style import ...`。

**3. 学术示意图**

```bash
cd skills/mathmodel-diagram
python3 code/templates/roadmap_5band.py content.json -o out.png   # PNG 300dpi + 同名矢量 PDF
python3 code/templates/roadmap_5band.py content.json --check      # 只做容量校验，不写文件
```

三条路径：套模板（5 个内置版式）、从零手写（算法/架构/机制图）、高保真复刻（照参考图重画）。

**4. 论文输出** — 复制 `skills/mathmodel-paper/templates/paper.tex` 到工作区填写占位，
`xelatex` 编译两遍生成 PDF，`pandoc` 转 Word，再用 `code/word_postprocess.py` 按竞赛口径微调版式；
摘要写法与检查项见 `templates/abstract-template.md`。

## 仓库结构

```
mathmodel-kit/
├── README.md                       # 中文文档（English: README_EN.md）
├── README_EN.md                    # 英文文档
├── LICENSE                         # Apache License 2.0
└── skills/
    ├── math-modeling-helper/       # 主技能：阶段零至阶段六工作流、代码与论文规范、评分口径
    │   └── SKILL.md
    ├── mathmodel-figure/           # 数据图表技能
    │   ├── code/style/             #   plot_style.py：色板/字号/尺寸/样式助手（唯一定义处）
    │   ├── code/templates/         #   20 个图模板，自带确定性模拟数据
    │   ├── code/tools/             #   render_template.py：id/别名/中文图题 → 复制并渲染
    │   ├── docs/guides/            #   出图规范、Nature 出图标准、定制配方
    │   └── examples/previews/      #   20 张模板效果预览（与模板同名对齐）
    ├── mathmodel-diagram/          # 学术示意图技能
    │   ├── code/common.py          #   绘图基元与容量校验
    │   ├── code/templates/         #   5 个 JSON 驱动模板
    │   ├── docs/guides/            #   方法论：authoring / replication / self-check
    │   └── examples/               #   每个模板的可复现示例（content.json + preview.png）
    └── mathmodel-paper/            # 论文输出技能
        ├── templates/              #   paper.tex 骨架、摘要模板
        └── code/                   #   word_postprocess.py：Word 版式后处理
```

## 依赖与自测环境

| 用途 | 依赖 |
|---|---|
| 数据图表 | Python 3 + `matplotlib` / `seaborn` / `numpy` / `pandas` |
| 学术示意图 | `matplotlib` + `numpy`；高保真复刻的标定脚本另需 `scipy` / `Pillow` |
| 论文编译 | `xelatex`（含中文字体支持）+ `pandoc` |
| Word 微调 | `python-docx` |
| 读取赛题附件 | `openpyxl`（旧版 `.xls` 需 `xlrd`）、`PyMuPDF` |

自测环境：Python 3.14 + matplotlib 3.10 + seaborn 0.13（Windows）；Linux/macOS 下若缺中文字体，
样式模块会告警并回退，图内中文可能显示为方框，请安装 `Noto Sans CJK SC`。

## 常见问题

| 现象 | 处置 |
|---|---|
| 图内中文显示方框 | 环境缺中文字体；安装 Microsoft YaHei / SimHei / Noto Sans CJK 后重渲染（`plot_style` 会显式告警而非静默出方框） |
| 轴标签里中文变方框、只有公式正常 | 禁止 mathtext 与中文混排：`"问题规模 $n$（个）"` 改为纯文本 `"问题规模 n（个）"` |
| 黑白打印分不清系列 | 靠明度阶梯、线型标记冗余与直接标注；红绿只出现在带 `↑/↓` 的增量上 |
| 想全局换配色 | 只改 `code/style/plot_style.py`，20 个模板与自绘图一并生效 |
| 渲染器提示未知模板 | 先 `--list` 查 id，或用英文别名、中文图题片段匹配 |

## 扩展与贡献

- 新增数据图表模板：按 [`mathmodel-figure/README.md`](skills/mathmodel-figure/README.md) 的扩展约定交付
  （模板脚本 + 目录加行 + 1:1 预览图 + 渲染器注册 + SKILL 清单）；
- 新增示意图模板：见 [`authoring.md`](skills/mathmodel-diagram/docs/guides/authoring.md)，
  几何常量需逐槽标定，交付前跑 `--check` 与九区盘点；
- 提交前请附最小可复现命令与渲染结果截图，便于核对风格一致性。

## 致谢

数据图表的 Nature 用色分工与「渲染后看图自检」的流程纪律，参考了社区仓库
[MathModeling-skills](https://github.com/zhnnky329/MathModeling-skills) 中 `math-figure-generator` 技能的设计思路。

## 许可证

[Apache License 2.0](LICENSE)
