# mathmodel-kit

> 数学建模竞赛一站式技能集：从赛题分析、模型构建、算法实现，到出版级图表与论文成稿。
>
> [English →](README_EN.md)

## 概述

套件由四个协同的 agent 技能组成：一个主技能编排全流程，三个专项技能分别负责数据图表、学术示意图与论文输出；各自可独立调用，组合即闭环。

| 技能 | 定位 |
|---|---|
| [`math-modeling-helper`](skills/math-modeling-helper/SKILL.md) | 主技能编排 · 赛题分析、算法优选、代码实现、论文写作与评分 |
| [`mathmodel-figure`](skills/mathmodel-figure/SKILL.md) | 数据图表 · 20 个 matplotlib 模板 + Nature 出图标准（模板外按标准现绘），一条命令产出 PNG / PDF / SVG |
| [`mathmodel-diagram`](skills/mathmodel-diagram/SKILL.md) | 学术示意图 · 5 个 JSON 驱动模板（路线图 / 框架图 / 流程图 / 问题分析图） |
| [`mathmodel-paper`](skills/mathmodel-paper/SKILL.md) | 论文输出 · LaTeX 骨架 → PDF → Word，及版式微调 |

## 特性

- **全流程覆盖** — 单一入口贯通「赛题理解 → 模型构建 → 算法实现 → 论文输出」，专项技能亦可按需独立调用。
- **出版级默认** — 数据图表 300 DPI、矢量优先，统一 Nature 风格配色（身份/方向/层级三色职责）与 Arial 无衬线字体；示意图逐槽中文字宽校验，超框即报错。
- **确定性与可复现** — 图表模板自带种子化模拟数据；示意图由 content JSON 驱动，产物可随时重渲、二次修改。
- **机器化质量门禁** — 容量校验非零退出、九区盘点、红队复审与自评分卡，共同约束交付质量。

## 仓库结构

```
mathmodel-kit/
├── README.md                   # 中文文档（英文见 README_EN.md）
├── LICENSE                     # Apache License 2.0
└── skills/
    ├── math-modeling-helper/   # 主技能：全流程规范与评分口径
    ├── mathmodel-figure/       # code/ 模板与样式 · docs/ 出图规范 · examples/ 效果预览
    ├── mathmodel-diagram/      # code/ 渲染器 · docs/ 方法论 · examples/ 可复现示例
    └── mathmodel-paper/        # LaTeX 骨架 · Word 微调脚本 · 摘要模板
```

## 快速开始

**安装** — 将 `skills/` 下需要的技能目录复制到 agent 的技能目录（如 `~/.claude/skills/`）：

```bash
cp -r skills/mathmodel-figure ~/.claude/skills/
```

**数据图表**

```bash
cd skills/mathmodel-figure
python3 code/tools/render_template.py --list             # 查看全部 20 个模板 id
python3 code/tools/render_template.py paired-raincloud   # 支持 id / 英文别名 / 中文图题
```

**学术示意图**

```bash
cd skills/mathmodel-diagram
python3 code/templates/roadmap_5band.py content.json -o out.png   # PNG 300dpi + 同名矢量 PDF
python3 code/templates/roadmap_5band.py content.json --check      # 只做容量校验，不写文件
```

**论文** — 复制 `templates/paper.tex` 至工作区填写占位，`xelatex` 编译两遍后以 `pandoc` 转 Word，再用 `code/word_postprocess.py` 微调版式；摘要写法见 `templates/abstract-template.md`。

## 依赖

- Python 3 与 `matplotlib` / `seaborn` / `numpy` / `pandas`
- 论文输出另需 `xelatex`（含中文字体支持）与 `pandoc`；Word 版式微调需 `python-docx`

## 许可证

[Apache License 2.0](LICENSE)
