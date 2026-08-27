# mathmodel-kit

数学建模竞赛（国赛/高教社杯）技能集：一个主技能编排「赛题分析 → 建模 → 求解 → 论文」全流程，三个专项技能分别负责数据图表、学术示意图与论文排版，可独立调用。

## 技能

| 技能 | 用途 |
|---|---|
| [`math-modeling-helper`](skills/math-modeling-helper/SKILL.md) | 主技能：赛题分析、算法优选、代码实现、论文写作与评分 |
| [`mathmodel-figure`](skills/mathmodel-figure/SKILL.md) | 数据图表：21 个 matplotlib 模板，一条命令产出 PNG/PDF/SVG |
| [`mathmodel-diagram`](skills/mathmodel-diagram/SKILL.md) | 学术示意图：5 个 JSON 驱动模板（技术路线图、框架图、流程图等） |
| [`mathmodel-paper`](skills/mathmodel-paper/SKILL.md) | 论文排版：LaTeX 骨架、pandoc 转 Word、python-docx 版式微调 |

## 使用

把 `skills/` 下需要的技能目录复制到 agent 的技能目录（如 `~/.claude/skills/`）即可。

依赖：Python 3 + `matplotlib` / `seaborn` / `numpy` / `pandas`；论文输出需 `xelatex` 与 `pandoc`（Word 微调需 `python-docx`）。

## License

[Apache License 2.0](LICENSE)
