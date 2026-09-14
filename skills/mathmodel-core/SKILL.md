---
name: mathmodel-core
description: 数学建模竞赛全流程主技能：按阶段零至阶段六编排全程（环境预检 → 赛题分析 → 工作目录 → 算法选择 → 代码实现 → 论文输出 → 评分优化），并把各环节路由到专项技能。用户提交赛题或提出建模需求时触发。算法与方法选型用 mathmodel-methods；论文写作与排版用 mathmodel-paper；数据图表与示意图用 mathmodel-figure / mathmodel-diagram；去 AI 与字符清理用 mathmodel-deai；结构自检与评分用 mathmodel-score。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 数学建模竞赛辅助技能

## 核心定位

专为数学建模国赛（高教社杯）设计，覆盖**赛题理解 → 模型构建 → 算法实现 → 论文输出**全流程。

**核心风格**：学术语态、逻辑严谨、创新性强、结果可验证

***

## 工作流（强制执行）

### 阶段零：环境预检（前置检查）

**在开始建模前，必须检查以下环境依赖是否可用**：

1. **编译环境**：
   - 检查 `xelatex` 是否可用（用于生成PDF）
   - 若不可用，提示安装 TeX Live 或 MiKTeX
2. **Python依赖**：
   - 检查 `python-docx`（用于 Word 版式后处理微调）
   - 检查 `PyMuPDF`（用于读取PDF数据；降 AI 技能 `mathmodel-deai` 的 `strip_invisible.py` PDF 清理模式亦依赖）
   - 检查 `openpyxl`（用于读取 .xlsx 数据）；若赛题附件含旧版 `.xls` 文件，另需 `xlrd`（openpyxl 不支持 .xls 二进制格式），缺失时安装 `pip install xlrd`
   - 若缺失，自动执行 `pip install python-docx pymupdf openpyxl`
3. **绘图库**：
   - 检查 `matplotlib`、`seaborn`、`numpy`、`pandas`
   - 若缺失，自动执行安装
   - 若需 plotly 静态导出（桑基图等），检查 `kaleido`；缺失时安装 `pip install kaleido`
4. **Word 转换工具**：
   - 检查 `pandoc` 是否可用（LaTeX→Word 转换必需，公式自动转 OMML 原生数学格式）
   - 若缺失，提示安装 pandoc（`winget install pandoc` 或官网下载），并提醒其为系统级安装、非 pip 可装
   - 示意图/流程图/架构图：使用 `mathmodel-diagram` 技能（matplotlib 渲染，无需额外系统依赖）

**输出**：环境状态报告（哪些可用、哪些已自动安装、哪些需用户手动处理）

### 阶段一：赛题分析与背景调研

**不输出给用户**，仅作为建模依据：

1. **背景调研（联网）**：使用联网检索工具查询赛题出处、实际应用场景、行业术语、数据含义等背景资料，对问题背景进行认真分析；检索结果作为建模依据与论文"问题背景与重述"章节的材料来源。
2. **问题本质**：核心问题是什么？属于哪类问题（优化/预测/评价/分类/微分方程）？
3. **已知条件**：可用数据、约束条件（资源/时间/物理）
4. **输出目标**：每个子问题需要什么形式的结果（数值/曲线/方案/排序）
5. **数据与问题对应关系**：逐问列出其使用的数据表/文件；若一题一个数据，则数据处理融入对应问题的分析与求解中；若所有问题共用一套数据，则论文单独设一级标题"五、数据处理"集中处理。

### 阶段二：工作目录创建

```bash
第X题_赛题简称/
└── answer/         # 所有建模产出统一存放于 answer 文件夹下
    ├── code/           # Python代码（按问题编号：q1_*.py, q2_*.py；含 plot_style.py 统一样式模块）
    ├── figures/
    │   ├── final/      # 交付图（语义命名：fig{图号}_{题型}_{内容}.png/pdf，≥300 DPI，须被论文 .tex 引用）
    │   └── tmp/        # 调试图（与正式版同品质 300 DPI；交付/打包前整体删除）
    └── paper/          # 论文（paper.tex + paper.pdf + paper.docx）
```

### 阶段三：算法选择（输出候选对比表，供用户选择）

1. **候选算法生成**：针对每个小问，结合问题类型、数据规模、约束条件，从 `mathmodel-methods` 的方法库中筛选 2–3 种可行算法，其中至少 1 种具有明显创新性（可引入交叉学科方法）。
2. **输出候选对比表**：以 Markdown 表格展示给用户，每行一个候选算法，列至少包含：

   | 候选算法 | 核心思路 | 创新度 | 可解释性 | 实现难度 | 预计耗时 | 精度/鲁棒性预期 |
   |---|---|---|---|---|---|---|
   | 例：熵权-TOPSIS | …… | 中 | 高 | 低 | 分钟级 | 中，对指标权重敏感 |

   评级用「高/中/低」，耗时按数据规模给出量级（秒级/分钟级/小时级）；表中须标注**推荐项及一句推荐理由**。
3. **用户选择**：等待用户确认或改选后再进入阶段四；用户明确委托代选时，按推荐项执行。

**论文中仅呈现最终采用的算法**：在“模型建立与求解”章节说明选择理由，简要提及 1 种未采用的替代方案及其不选原因，无需输出完整对比表格。

**要求**：

- **算法选型核心原则：拟合性优先于高级性**——首选与问题结构、数据规模、约束条件最匹配的算法（保证可求解、结果可靠、可解释），再在匹配基础上考虑创新性；禁止为炫技强行引入与问题不适配的高深算法，导致求解困难或结论不可信
- 对比表基于本题的数据规模与约束如实评估，禁止夸大创新度或低估实现难度
- 最终方案的数学描述使用学术语态，公式独立呈现
- 形成逻辑闭环，控制字数

### 阶段四：代码实现

**技术栈（按用途分类，无先后优先级，按题目需要选用）**：

- 基础数值与可视化：numpy, scipy, pandas, matplotlib, seaborn
- 优化建模：pulp, cvxpy, scipy.optimize
- 机器学习：scikit-learn, xgboost
- 数据读取：PyMuPDF（PDF）、openpyxl（.xlsx）、pandas

**代码规范**：

- 完整可运行，保存至 `code/` 文件夹
- 使用 numpy 向量化操作
- 关键参数通过注释说明
- 输出清晰的结果摘要
- 可视化保存至 `figures/final/`，学术风格，≥300 DPI；数据图表优先复用 `mathmodel-figure` 技能模板（统一样式模块 `plot_style.py` 随模板自动复制到工作区），模板不匹配时按该技能的 `docs/guides/nature-standard.md` 现绘，示意图用 `mathmodel-diagram` 技能

### 阶段五：论文输出

**输出物（必须同时生成 PDF 与 Word）**：

- `.tex` 源文件 + `.pdf` 成品论文
- `.docx` Word 文档
- 存放至 `paper/` 文件夹
- 图片路径使用相对路径 `../figures/final/fig2_surface_obj.png`（语义命名，见阶段二目录规范）

**生成命令（PDF 与 Word 均需执行）**：

```bash
# 0. 降 AI 门禁（脚本在 mathmodel-deai 技能 code/ 目录下执行）：
python3 code/check_phrasing.py paper.tex            # 词表级：查模板腔/套话/空泛，命中即改写
python3 code/check_style.py paper.tex               # 结构级：查长句/句式重复/段落节奏/小数位
python3 code/strip_invisible.py --clean paper.tex   # 字符级：编译前清源文件，从源头杜绝零宽/不可见字符

# 1. 生成 PDF
cd paper
xelatex -interaction=nonstopmode paper.tex
xelatex -interaction=nonstopmode paper.tex

# 2. 生成 Word（pandoc 将 LaTeX 转为 .docx，公式自动转为 Word 原生数学格式 OMML）
pandoc paper.tex -o paper.docx
# 若公式/表格版式需进一步微调，再用 python-docx 后处理（禁止用文本模拟公式）

# 3. 交付门禁：两道表述级检查须退出 0；最终 PDF 与 Word 都必须清理并复检零宽/不可见字符（退出码须为 0）
python3 code/check_phrasing.py paper.tex
python3 code/check_style.py paper.tex
python3 code/strip_invisible.py --clean paper.pdf paper.docx
python3 code/strip_invisible.py paper.pdf paper.docx
```

**技术栈**：

- LaTeX：xelatex 编译
- Word：pandoc 从 LaTeX 转换生成 .docx（公式自动转为 OMML，见上方生成命令）
- Word 版式微调：python-docx 补充页眉留空/页码/字体（公式勿用 python-docx 手工插入）

### 阶段六：论文评分与优化（强制执行）

论文生成后，**必须**调用专项技能 `mathmodel-score` 做交付前自检与百分制评分：**$S \geq 85$ 且无一票否决方可最终输出**。

- 五维权重与扣分细则：`mathmodel-score/docs/rubric.md`（摘要 30 / 算法模型 20 / 创新性 20 / 写作 15 / 排版 15，合计 100）
- 章节结构门槛（评分前置）：`python3 code/check_chapters.py <论文文件>`（hard 未过先补齐、不计分；逐条判据见 `mathmodel-score/docs/chapter-checklist.md`，可用 `--rules mcm` 切美赛口径）
- 交付前逐项自检：`mathmodel-score/docs/self-check.md`（致命 / 严重 / 中等 / 轻微四级）
- 评分卡校验与评分表渲染：`python3 code/score_card.py scorecard.json`（退出码 0 达标 / 1 需优化 / 2 输入错误；`--list-dimensions` 查看维度契约）
- 优化循环：$S < 85$ 时按扣分从高到低逐项修改后重新评分；**熔断 3 轮**，仍未达标则输出当前版本并标注"未达 85 分标准，需人工复核"；任一维度为 0 或触发一票否决（身份信息/页眉等红线）时强制处理

评分流程、评分表模板与全部扣分标准以 `mathmodel-score` 技能为唯一权威（本阶段只列强制项）。

***

## 核心能力

### 1. 建模方法与算法选型（引用专项技能）

算法库、选型依据与实现范式已拆分到专项技能 `mathmodel-methods`，**方法名与适用场景以该技能为唯一出处**，
本节不复制方法清单：

- 方法清单（问题族索引 + 九类方法 + 收录标准）：`mathmodel-methods/docs/method-library.md`
- 选型流程、候选对比表、问题特征对照、按问题类型的验证方式：`mathmodel-methods/docs/selection-guide.md`
- 推荐库、最小可运行骨架、实现纪律：`mathmodel-methods/docs/implementation-guide.md`

阶段三（算法选择）与阶段四（代码实现）按上述口径执行；本技能只保留三条强制原则：
**拟合性优先于高级性**、**方法梯度（能用简单的不用复杂的）**、
**创新须回答「解决了旧方法解决不了的什么问题」**。

***

### 2. 算法实现与 Word 后处理（引用专项技能）

- 算法实现规范（推荐库速查、GA/SA/0-1 规划与数据读取的最小可运行骨架、输出要求）：
  `mathmodel-methods/docs/implementation-guide.md`
- Word 后处理（pandoc 转换后的版式微调，含「只调样式、不重建内容」红线）：
  `mathmodel-paper/docs/typesetting-rules.md`

***

### 3. 论文写作规范（引用专项技能）

论文结构、章节编号、标题命名、摘要格式与五段式模板、模型建立三步法与表达五条、公式使用规范、
分析推导与模型求解规范、模型评价与附录规范、正文语言表述规范，均已拆分到专项技能 `mathmodel-paper`：

- **唯一权威出处**：`mathmodel-paper/docs/writing-rules.md`
- 正文语言表述与去 AI 口径以 `mathmodel-deai/docs/deai-rules.md` 为准

写作阶段只记三条硬约束：每个问题给出**具体数值结果**（小数点后 2–4 位）与误差 / 稳健性分析；
核心公式（目标函数、关键约束、状态方程）独立编号，检测量公式首次定义一次、后续只引用指标名与数值；
每问结尾给出结论段（直接回答 + 关键数值 + 达标判断）。

***

### 4. 可视化规范（引用专项技能）

本章全部图表细则已拆分至专项技能，出图时按下表调用，**规范条文以 `mathmodel-figure/docs/guides/visualization-rules.md` 为唯一权威出处**：

| 需求 | 使用技能 |
| ---- | ---- |
| 数据图表（三维曲面/热力图/拟合+残差/收敛/Pareto/折线/柱状/箱线/环形/条形/云雨/ROC/Taylor/SHAP 等 20 种模板） | `mathmodel-figure`：`python3 code/tools/render_template.py <模板id>` 直接渲染；统一样式模块 `code/style/plot_style.py`（色板/字体回退/save_fig）随模板复制到工作区 |
| 模板库外的自定义图型（等高线、相图、堆叠面积、雷达、甘特、龙卷风、平行坐标、桑基、地图热力、小多图、双轴图等） | `mathmodel-figure`：按 `docs/guides/nature-standard.md` 的 Nature 出图标准现绘（六条硬标准 + 最小起图骨架 + 图型选择表），样式仍取自 `code/style/plot_style.py` |
| 学术示意图（技术路线图、研究框架图、阶段流程图、任务流水线图、**第二章问题分析流程图**、算法/系统架构图） | `mathmodel-diagram`：5 个 JSON 驱动模板（含 `problem-flow`），matplotlib 渲染产出 PNG(300DPI)+PDF |

**图型按需求选，不过度依赖模板库**：模板只是省时间的加速器，不是可选图型的边界。
先问「这份数据是什么结构、要论证什么结论、哪种图型最能证明它」，再决定套模板还是现绘；
20 个模板不匹配就按 `nature-standard.md` 起图，**禁止为套用模板而改数据语义、
禁止把不相干的图硬凑成多子图**，也禁止用图型堆砌代替论证。

**全文风格统一（模板图与现绘图一律同一套样式）**：颜色与字号只从 `plot_style.py` 取，
同一方法在全文所有图里同色（本文=主角蓝、对照方法=橙/紫/青、基准=中灰、背景信息=浅调），
坐标框架走 `style_axes()`、多子图标号走 `add_panel_label()`、导出走 `save_fig()`；
出图后按 `visualization-rules.md` 的渲染自检清单看产物，代码跑通不算通过。

**硬性要求（全流程强制，与专项技能一致）**：每道小题至少 1 张彩色图（建议 2–3 张）；第二章问题分析必须插入问题分析图（用 `mathmodel-diagram` 的 `problem-flow` 模板）；全文建议 6 张以上、保底 4 张；图片紧邻对应分析文字就近插入（图题在图下方），禁止集中堆放在文末；每张图前后必须有文字引导与解读；拟合结果与误差分析必须可视化；所有图表 ≥300 DPI 出版级质量（密度类图分级策略见 visualization-rules.md）；配色、线型、图例、黑白打印等细则见 visualization-rules.md。

***

### 5. 排版规范（LaTeX）（引用专项技能）

页面设置、排版强制规范（匿名与保密、图片完整性、编码、分页、公式与字体、图表、caption 等）
与 LaTeX 骨架说明见 `mathmodel-paper/docs/typesetting-rules.md`（唯一权威），可复制骨架见
`mathmodel-paper/templates/paper.tex`。

一票否决项（本技能保留）：摘要页、正文、附录任何位置不得出现参赛者姓名、学校、赛区、队号、
指导教师等身份信息，且全文禁止页眉。

***

### 6. 参考文献规范（引用专项技能）

GB/T 7714 著录格式、引用数量建议与**引用查证流程**见 `mathmodel-paper/docs/references.md`（唯一权威）。
硬约束：正文引用 5–8 篇，至少 2 篇近 5 年、1 篇英文；所有引用必须逐条在线核实，严禁编造。

***

### 7. 论文质量自检与评分（引用专项技能）

论文的**交付前自检**与**百分制评分**已收敛到专项技能 `mathmodel-score`，**唯一权威出处**：`mathmodel-score/docs/self-check.md`（四级自检清单）与 `mathmodel-score/docs/rubric.md`（五维评分细则）。写作阶段只需记住以下强制项，评分与自检一律按该技能执行：

- **结构门槛**：章节结构 hard 项未过（缺符号说明三线表、缺模型评价优缺点、附录缺可运行源程序、正文含目录、出现身份信息等）先补齐，不进入评分；判据见 `mathmodel-score/docs/chapter-checklist.md`
- **五维权重**：摘要 30 / 算法模型 20 / 创新性 20 / 写作 15 / 排版 15，合计 100；**$S \geq 85$ 方可最终输出**
- **一票否决**：出现参赛者身份/学校/赛区信息或页眉等红线，直接淘汰、不计分，不进入优化循环
- **熔断**：最大优化轮次 3 轮；3 轮后仍未达标即输出当前版本并标注"未达 85 分标准，需人工复核"
- **自检四级**：致命（匿名/编码）→ 严重（文件完整性、PDF/Word 一致性、摘要与正文一致、模型选择理由、附录、符号、文献查证）→ 中等（公式图表完整性、正文语言、误差分析）→ 轻微（表达规范）
- **评分卡**：按五维填写评分卡 JSON，用 `python3 code/score_card.py scorecard.json` 校验并渲染评分表（退出码 0 达标 / 1 需优化 / 2 输入错误；`--list-dimensions` 查看维度契约）

完整扣分细则、评分表模板与优化触发规则见 `mathmodel-score/docs/rubric.md`；逐项自检清单见 `mathmodel-score/docs/self-check.md`。

***

## 使用方式

**触发场景**：

1. 用户上传赛题文本或粘贴赛题内容
2. 用户提问"分析这道题"或"帮我建模"
3. 用户要求推荐算法或编写代码
4. 用户提交论文草稿要求润色
5. 用户要求先联网查证赛题背景再进行分析与建模

**输出风格**：

- 默认使用中文输出
- 代码块标注语言类型
- 表格清晰对齐
- 关键结论突出显示

***

## 快速参考

算法选择速查、算法实现速查与问题递进关系见 `mathmodel-methods` 技能
`docs/selection-guide.md`（问题特征 → 推荐方法、问题递进关系、常见误用）。

### 常见错误速查

| 错误类型      | 解决方案                                |
| --------- | ----------------------------------- |
| 中文乱码      | 使用 xelatex，删除 inputenc              |
| 图片文字不全    | 设置 SimHei，使用 bbox\_inches='tight'   |
| 图片中文显示方框  | 缺字体环境用字体检测回退（`mathmodel-figure` 的 `plot_style.pick_cjk_font`），安装 SimHei 或 Noto Sans CJK |
| 折线图曲线过多难区分 | 同图≤5条，线型+标记区分，超限分图         |
| 性能对比图Y轴不从0起 | 强制 `ax.set_ylim(0, ...)`，避免视觉误导    |
| 黑白打印分不清组别 | 用学术低饱和配色+明暗/透明度区分；多组年份可用横线/竖线纹理 |
| 只会套模板、图型与数据不匹配 | 图型按数据与结论选：按 `mathmodel-figure/docs/guides/nature-standard.md` 现绘，样式仍取自 `plot_style.py`，保证与模板图同风格 |
| 文字超出纸张    | 使用 seqsplit，tabularx，[H]定位         |
| caption报错 | 使用 font=small，禁止 font={font=10.5pt} |
| 假设用列表非表格   | 改用 tabular 三线表，表题在上方，含合理性说明        |
| 假设表格显示不全   | `tabular`的`l`列不换行，改用`tabularx`的`X`列  |
| 正文AI痕迹过重（模板腔/套话/衔接生硬） | 见 `mathmodel-paper/docs/writing-rules.md`「正文语言表述规范」：直入主题、衔接句带信息量、结论个性化 |
| Word中公式显示为普通文本/乱码 | 用 pandoc 从 paper.tex 生成 .docx，公式自动转 OMML 原生数学格式 |
| 公式过度堆砌/检测量公式重复列式 | 见 `mathmodel-paper/docs/writing-rules.md`「公式使用规范」：推导从简、检测量公式仅首次定义 |



