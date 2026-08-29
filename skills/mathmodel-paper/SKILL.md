---
name: mathmodel-paper
description: 数学建模论文排版模板工具链：LaTeX 论文骨架（paper.tex）、pandoc 转 Word、python-docx 版式微调（页眉留空/页码/中文字体/三线表）、不可见 Unicode/零宽字符清理（strip_invisible.py）、摘要写作模板。当用户要论文模板或骨架、生成/微调 Word 论文版式、清理零宽字符、写摘要时触发。建模、算法选择、正文写作规范、评分自检请改用主技能 math-modeling-helper。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 数学建模论文模板与输出工具链

## 定位

本技能是 `math-modeling-helper` 主技能的**配套输出物工具链**，只管「论文怎么排版、怎么转成 PDF/Word」：

- 只管：LaTeX 论文骨架、编译与转换命令、Word 版式微调脚本、摘要写作模板、页面设置与匿名红线速查。
- 不管：赛题分析、算法选择、代码实现、正文语言表述、质量自检与百分制评分——这些**规范条文与评分口径一律以主技能 `math-modeling-helper` 为准**，本技能只是其可执行落地件。
- 与本技能冲突时以主技能规范为准；本技能内容全部提取自主技能，未新增任何规范。

## 快速流程

1. 复制 `templates/paper.tex` 到工作区 `paper/paper.tex`，按注释占位处填写题目、摘要、章节、参考文献；图片用相对路径 `../figures/final/xxx.png`。摘要写法见 `templates/abstract-template.md`。填写完成后先清理源文件（从源头杜绝零宽字符进入产物）：

   ```bash
   python3 code/strip_invisible.py --clean paper/paper.tex
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

5. 不可见字符清理（**强制交付门禁**，最终 PDF 与 Word 都必须运行；字符集移植自 watermarks-remover 的 Layer A：零宽家族/bidi 控制/tag 字符/变体选择符/私用区等）：

   ```bash
   python3 code/strip_invisible.py --clean paper/paper.pdf paper/paper.docx   # 就地清理（留 .bak）
   python3 code/strip_invisible.py paper/paper.pdf paper/paper.docx           # 复检，必须退出码 0
   ```

   PDF 模式需要 PyMuPDF（`pip install pymupdf`）；tex/docx 模式仅用标准库。清理后复检仍报 `CLEANED-RESIDUAL` 时不得交付，回查 tex 源与转换链。

6. 核对 PDF 与 Word 一致性（主技能第 7 章「PDF 与 Word 格式一致性检查」）：题目三号黑体居中、摘要标签四号黑体、正文小四宋体 1 倍行距首行缩进 2 字符、一级标题四号黑体居中、三线表无竖线、图题在下表题在上、页码位置一致、图表编号与数值一一对应。

已知限制：pandoc 对 ctex/xelatex 专用宏包解析有限，转换前需用 pandoc 支持的等价写法或轻量预处理（如临时替换 ctex 为 CJK 包），转换后必须核对并修正中文字体/字号与三线表。

## 页面设置速查

| 项目    | 设置                                         |
| ----- | ------------------------------------------ |
| 纸张    | A4，纵向                                      |
| 页边距   | 四边2.5cm（上/下/左/右均为2.5cm）                   |
| 论文题目  | 黑体，三号（16pt），居中                             |
| 一级标题  | 黑体，四号（14pt），居中，段前段后各0.5行                   |
| 二级标题  | 黑体，小四（12pt），左对齐                            |
| 三级标题  | 黑体，小四（12pt），左对齐                            |
| 中文正文  | 宋体，小四（12pt），1倍行距，首行缩进2字符                   |
| 西文/数字 | Times New Roman，小四（12pt）                   |
| 数学公式  | Times New Roman，小四，居中，右侧编号；跨行公式整体居中、编号在右侧 |
| 图表标题  | 宋体，五号，居中（图下表上）                             |
| 页码    | 页尾居中，从第一页（摘要页）开始编号，摘要页即为第1页；全文禁止页眉                     |
| 总页数   | 正文25-30页，附录不做页数要求                        |

## 匿名红线清单（一票否决，违反即取消评奖资格）

- [ ] 摘要页、正文、附录（含支撑材料）任何位置**无**参赛者姓名、所在学校、赛区、参赛队号、指导教师等身份信息
- [ ] **无页眉**：页眉区域完全留空，`\renewcommand{\headrulewidth}{0pt}`，无文字、图片或横线
- [ ] 作者区留空：`\author{}`、`\date{}`，`\maketitle` 不显示作者与日期
- [ ] 页脚仅居中页码，无学校/队号等身份信息
- [ ] 图片、表格、代码注释、文件名等位置同样不泄露身份信息（**逐一检查图片中是否有学校水印/名称**）
- [ ] 页码从第一页（摘要页）开始连续编号，摘要页为第 1 页，页尾居中；`\maketitle` 后必须加 `\thispagestyle{fancy}` 覆盖默认 plain 样式
- [ ] 摘要页：题目 + 摘要 + 关键词同页，摘要 800-1000 字，关键词后 `\newpage`，正文从第 2 页起
- [ ] Word 版式与 PDF 同样满足以上各条（`code/word_postprocess.py` 已自动清空页眉并写入居中页码域）

## 目录结构

```
mathmodel-paper/
├── SKILL.md                    # 本文件：定位 + 快速流程 + 页面速查 + 匿名红线
├── README.md                   # 目录组织说明
├── code/
│   ├── word_postprocess.py     # pandoc 转换后的 Word 版式微调脚本（可执行，argparse 接收 docx 路径）
│   └── strip_invisible.py      # 不可见 Unicode/零宽字符清理（tex/docx/pdf，Layer A 字符集）
└── templates/
    ├── paper.tex               # LaTeX 论文骨架（可复制填写，含全部规范注释）
    └── abstract-template.md    # 摘要写作模板 + 关键要求 + 摘要页分页规则
```
