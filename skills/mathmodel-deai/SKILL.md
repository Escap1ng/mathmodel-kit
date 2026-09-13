---
name: mathmodel-deai
description: 降 AI 模块：论文去 AI 化与交付前字符清理。词表级用 check_phrasing.py + 词表揪出模板腔、套话、空泛与伪洞察句式；结构级用 check_style.py 矫正过长被动句、句式重复、过渡词密度、段落节奏与结果小数位，并给出风险等级；字符级用 strip_invisible.py（Layer A 字符集）清除零宽字符、bidi 控制、tag 字符等不可见 Unicode，覆盖 .tex/.docx/.pdf。当用户要求去 AI 味、降低 AI 痕迹、去除零宽/不可见字符、改写模板腔与套话、优化句式与段落节奏、给论文加个性化表述时触发。建模与评分口径以主技能 mathmodel-core 为准，排版与论文骨架用 mathmodel-paper。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 降 AI 模块（去 AI 化 + 字符清理）

## 定位

本技能是 `mathmodel-core` 主技能的**配套质检与清理件**，只管「论文读起来像不像人写的、带不带隐写字符」：

- **词表级**：`code/check_phrasing.py` 按词表 `code/phrasing-blacklist.json` 扫出模板腔、套话、空泛、伪洞察等 AI 痕迹用词与句式（含英文规则 `en-slop-*`，用于英文摘要与图注），命中即退出 1，改写后复检。
- **结构级**：`code/check_style.py` 检查过长被动句、句式重复、过渡词密度、长短句比例、相邻段落节奏与结果小数位，并给出 `低/中/高/极高` 风险等级；逻辑自审、图表与文献规范以人工核对清单执行。
- **字符级**：`code/strip_invisible.py` 清除零宽字符、bidi 控制、tag 字符、变体选择符等不可见 Unicode（字符集移植自 watermarks-remover 的 Layer A），覆盖 `.tex` / `.docx` / `.pdf`。
- 不管：赛题分析、算法选择、代码实现、论文骨架与版式、百分制评分——这些分别以主技能 `mathmodel-core`、`mathmodel-paper`、`mathmodel-score` 为准。
- **规范条文以本技能 `docs/deai-rules.md` 为唯一权威出处**；主技能只保留强制项摘要并指向本文件，避免两处规范漂移。
- **边界**：降 AI 只处理表述与字符，不改动数学模型、数据与结论；去 AI ≠ 口语化，个性化判据是「只有这篇论文写得出」。

## 快速流程

1. **表述级检查**（论文正文与摘要定稿后，词表级与结构级依次跑）：

   ```bash
   python3 code/check_phrasing.py paper/paper.tex          # 词表级：模板腔/套话/空泛/伪洞察，命中即退出 1
   python3 code/check_style.py paper/paper.tex             # 结构级：句长/句式重复/过渡密度/段落节奏/小数位，命中即退出 1
   python3 code/check_phrasing.py --list-rules              # 查看词表与规则
   python3 code/check_style.py --list-metrics               # 查看结构指标与阈值
   ```

   命中处按输出里的 `→` 提示改写（补具体数值、给出处、拆长句、拉开段落节奏等），改完复检至双双退出 0。
   词表规则带 `max_per_document` 的是**频次上限**，超出部分才算命中；结构指标在样本过小时自动跳过。
   词表是数据，**加词只改 `code/phrasing-blacklist.json`**；结构阈值写在 `check_style.py` 头部常量，调整需同步文档。

2. **字符级清理**（编译前清源文件，交付前清产物）：

   ```bash
   python3 code/strip_invisible.py --clean paper/paper.tex                    # 编译前：从源头杜绝
   python3 code/strip_invisible.py --clean paper/paper.pdf paper/paper.docx   # 交付门禁：就地清理（留 .bak）
   python3 code/strip_invisible.py paper/paper.pdf paper/paper.docx           # 复检，必须退出码 0
   ```

   PDF 模式需 PyMuPDF（`pip install pymupdf`）；tex/docx 模式仅用标准库。**最终 PDF 与 Word 都必须清理并复检**，复检仍报 `CLEANED-RESIDUAL` 不得交付。

3. **个性化补写**：按 `docs/deai-rules.md` 第四节，在方法选型、模型评价、结果分析、推广展望处补上判断痕迹、量化局限、机理阐释、可核实的现实锚定与三方向展望——全部以本题数据与逻辑为支撑。

## 强制项摘要（正文写作与摘要）

- 章节开头直入主题，禁 `随着…的快速发展` / `在当今社会` / `众所周知` 式模板腔
- 过渡句必须携带信息量，禁纯形式衔接；`首先…其次…再者…最后` 连接链全文至多一组，仅用于单一求解流程内部
- 无依据空泛词（`很明显`、`大量`、`效果很好`）、含糊收尾（`一定程度上`、`有望`、`大概`）、模板腔结果表述（`较为理想`、`具有参考价值`）一律改为具体数值与具体场景
- 权威含糊（`研究表明`、`专家认为`）必须补可核实出处，找不到就删（宁缺毋假）
- 空泛形容词（`至关重要`、`显著提升`）、冗长连接（`简而言之`、`不得不说`）、模板化目的句（`为了更好地…`、`旨在…`）一律改为专业表述 + 数值或机制
- 句式与段落节奏：拆分 >25 字被动句；同类句式连续 ≤3 次；每段过渡词 ≤2 个；相邻段落字数差异 ≥20%；结果统一保留 2-4 位小数
- 摘要开头必须有实质钩子（矛盾/数字/困境），禁用 `本文对…问题进行了深入研究` 式模板腔
- 逻辑与风格：至少 2-3 处客观自审（假设→失效情形→量化影响→适用边界）；结论须有数据/理论支撑；不确定结果明确标注范围
- 全文跑 `check_phrasing.py` 与 `check_style.py` 双双退出 0；风险等级为「高/极高」时不得交付；每处改写保留「原句→改句→依据」痕迹
- 最终 PDF 与 Word 跑 `strip_invisible.py` 复检退出 0

完整条文、负面清单、五段式摘要去模板化对照表、结构级十项升级细则与个性化表述规范见 [`docs/deai-rules.md`](docs/deai-rules.md)。

## 目录结构

```
mathmodel-deai/
├── SKILL.md                       # 本文件：定位 + 快速流程 + 强制项摘要
├── README.md                      # 目录组织说明
├── code/
│   ├── check_phrasing.py          # 词表级检查器（词表驱动，argparse 入口）
│   ├── phrasing-blacklist.json    # 去 AI 词表与句式规则（单一事实源）
│   ├── check_style.py             # 结构级检查器（句长/句式/段落/小数位 + 风险等级）
│   └── strip_invisible.py         # 字符级清理器（tex/docx/pdf，Layer A 字符集）
├── docs/
│   ├── deai-rules.md              # 降 AI 规范（唯一权威）
│   └── no-ai-slop-reference.md    # 英文参考：AI slop 模式清单（整理自 petergyang/no-ai-slop，MIT）
└── examples/
    ├── clean-sample.tex           # 正例：合规写法，两检查器都应零命中
    ├── slop-sample.tex            # 反例：中文词汇/句式痕迹密集，供 check_phrasing 冒烟
    ├── style-slop-sample.tex      # 反例：结构痕迹密集，供 check_style 冒烟
    ├── clean-sample-en.md         # 正例（英文）：合规写法
    └── slop-sample-en.md          # 反例（英文）：en-slop-* 规则密集
```

## 与其他技能的关系

| 技能 | 关系 |
|---|---|
| `mathmodel-core` | 主技能。正文语言表述规范中「去 AI 化要求」「负面清单」「个性化表述规范」已收敛到本技能 `docs/deai-rules.md`，主技能保留强制项摘要并指向本文件 |
| `mathmodel-paper` | 论文骨架与版式。编译前清 `.tex` 源、交付前清 PDF/Word，均调用本技能 `code/strip_invisible.py` |
| `mathmodel-figure` / `mathmodel-diagram` | 出图。图表解读文字同样受本技能表述级规则约束（无空泛、图表不孤立） |
