---
name: mathmodel-paper
description: 数学建模论文写作与排版技能：论文写作规范（结构、摘要五段式、模型建立与求解、公式、模型评价、附录、正文语言表述）+ LaTeX 骨架与页面设置、匿名红线 + pandoc 转 Word 与 python-docx 版式微调 + 参考文献著录与查证（GB/T 7714）。当用户要写论文、要论文模板或骨架、写摘要、按竞赛口径排版、生成或微调 Word 论文、处理参考文献时触发。赛题分析、算法选择与代码实现改用 mathmodel-core / mathmodel-methods；去 AI 与零宽字符清理改用 mathmodel-deai；结构自检与评分改用 mathmodel-score；数据图表与示意图改用 mathmodel-figure / mathmodel-diagram。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 数学建模论文写作与排版（mathmodel-paper）

本技能是论文域的唯一入口，覆盖**内容规范**（写什么）与**排版输出**（怎么排、怎么转）。
写作、排版与参考文献条文以本技能 `docs/` 为唯一权威。

## 定位

- **管**：论文写作规范、摘要写法、模型建立与求解表述、公式与附录规范、正文语言表述；
  LaTeX 骨架与页面设置、匿名红线、pandoc 转 Word、python-docx 版式微调；参考文献著录与查证。
- **不管**：赛题分析、算法选择与代码实现（`mathmodel-core` / `mathmodel-methods`）；去 AI 化与零宽字符清理
  （`mathmodel-deai`）；结构自检与百分制评分（`mathmodel-score`）；数据图表与示意图
  （`mathmodel-figure` / `mathmodel-diagram`）。
- 正文语言表述与去 AI 口径以 `mathmodel-deai` 为准；与 `mathmodel-score` 的章节结构契约冲突时以对方为准。

## 文档地图

| 你要做什么 | 看哪份 |
|---|---|
| 论文结构、摘要五段式、模型建立与求解、公式、评价、附录、语言表述 | [`docs/writing-rules.md`](docs/writing-rules.md) |
| 页面设置、排版强制规范、匿名红线、LaTeX 骨架说明、Word 后处理 | [`docs/typesetting-rules.md`](docs/typesetting-rules.md) |
| 参考文献格式、数量建议、引用查证流程 | [`docs/references.md`](docs/references.md) |
| 摘要写作模板 | [`templates/abstract-template.md`](templates/abstract-template.md) |
| LaTeX 骨架 | [`templates/paper.tex`](templates/paper.tex) |
| 章节结构自检与评分 | [`mathmodel-score`](../mathmodel-score/SKILL.md) |
| 去 AI 化与零宽字符清理规范 | [`deai-rules.md`](../mathmodel-deai/docs/deai-rules.md) |

## 快速流程

1. 复制 `templates/paper.tex` 到工作区 `paper/paper.tex`，按注释占位处填写题目、摘要、章节、参考文献；图片用相对路径 `../figures/final/xxx.png`。摘要写法见 `templates/abstract-template.md`。填写完成后先清源文件（降 AI 技能 `mathmodel-deai`，从源头杜绝零宽/不可见字符进入产物）：

   ```bash
   python3 ../mathmodel-deai/code/strip_invisible.py --clean paper/paper.tex
   ```

2. 编译 PDF（**两遍**，交叉引用与编号才稳定）：

   ```bash
   cd paper
   xelatex -interaction=nonstopmode paper.tex
   xelatex -interaction=nonstopmode paper.tex
   ```

3. 转 Word（pandoc 自动把公式转为 OMML 原生数学格式）：

   ```bash
   pandoc paper.tex -o paper.docx
   ```

4. 版式微调（原地覆盖写回；只做样式，不重建内容）：

   ```bash
   python3 code/word_postprocess.py paper/paper.docx   # 省略参数时默认 paper/paper.docx
   ```

   ⚠️ 该脚本**仅用于 pandoc 转换后的版式微调**（页眉留空、页码页脚、中文字体、三线表核对），
   **禁止 `add_paragraph`/`add_table`/`add_page_break` 新增或重建内容，禁止手工插入公式**，
   否则 Word 中会丢失全部数学公式或在文档后追加重复全文。

5. 降 AI 门禁（**强制交付门禁**）：词表级查模板腔/套话、结构级查句式与段落节奏、字符级清零宽/不可见 Unicode，均由降 AI 技能 `mathmodel-deai` 负责（规范见其 `docs/deai-rules.md`，字符集移植自 watermarks-remover 的 Layer A）：

   ```bash
   python3 ../mathmodel-deai/code/check_phrasing.py paper/paper.tex           # 词表级：命中即改写（退出码 0 才算过）
   python3 ../mathmodel-deai/code/check_style.py paper/paper.tex              # 结构级：句长/句式/段落节奏/小数位
   python3 ../mathmodel-deai/code/strip_invisible.py --clean paper/paper.pdf paper/paper.docx   # 就地清理（留 .bak）
   python3 ../mathmodel-deai/code/strip_invisible.py paper/paper.pdf paper/paper.docx           # 复检，必须退出码 0
   ```

   PDF 模式需要 PyMuPDF（`pip install pymupdf`）；tex/docx 模式仅用标准库。清理后复检仍报 `CLEANED-RESIDUAL` 时不得交付，回查 tex 源与转换链。

6. 核对 PDF 与 Word 一致性（`mathmodel-score/docs/self-check.md` 的「PDF 与 Word 格式一致性检查」）：题目三号黑体居中、摘要标签四号黑体、正文小四宋体 1 倍行距首行缩进 2 字符、一级标题四号黑体居中、三线表无竖线、图题在下表题在上、页码位置一致、图表编号与数值一一对应。

已知限制：pandoc 对 ctex/xelatex 专用宏包解析有限，转换前需用 pandoc 支持的等价写法或轻量预处理（如临时替换 ctex 为 CJK 包），转换后必须核对并修正中文字体/字号与三线表。

## 交付前红线（一票否决）

完整清单与依据见 [`docs/typesetting-rules.md`](docs/typesetting-rules.md)；交付前至少确认：

- [ ] 摘要页、正文、附录任何位置**无**参赛者姓名、学校、赛区、队号、指导教师等身份信息（含图片水印/文件名）
- [ ] **全文无页眉**，页脚仅居中页码，页码从摘要页（第 1 页）起连续编号
- [ ] 摘要页：题目 + 摘要 + 关键词同页，摘要 800–1000 字，关键词后 `\newpage`
- [ ] Word 版式与 PDF 一致，且同样满足以上各条
- [ ] 参考文献逐条在线核实、无编造

## 目录结构

```
mathmodel-paper/
├── SKILL.md                    # 本文件：定位 + 文档地图 + 快速流程 + 交付红线
├── README.md                   # 目录组织说明
├── code/
│   └── word_postprocess.py     # pandoc 转换后的 Word 版式微调脚本（可执行，argparse 接收 docx 路径）
├── docs/
│   ├── writing-rules.md        # 论文写作规范（唯一权威）
│   ├── typesetting-rules.md    # 排版规范（唯一权威，含 Word 后处理）
│   └── references.md           # 参考文献规范（唯一权威）
└── templates/
    ├── paper.tex               # LaTeX 论文骨架（可复制填写，含全部规范注释）
    └── abstract-template.md    # 摘要写作模板 + 关键要求 + 摘要页分页规则
```
