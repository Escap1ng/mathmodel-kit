---
name: mathmodel-score
description: 论文评分与质量自检模块：按百分制五维（摘要 30 / 算法模型 20 / 创新性 20 / 写作 15 / 排版 15）对论文打分，交付前逐项自检并给出扣分明细、优化轮次与达标判定。用 score_card.py 把评分卡 JSON 校验并渲染成评分表（达标线 85，一票否决直接淘汰，熔断 3 轮）。当用户要求给论文打分、自检、生成评分表、评估能否交付、判断 AI/合规风险时触发。建模与写作规范以主技能 mathmodel-core 为准，版式与去 AI 分别见 mathmodel-paper / mathmodel-deai。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 论文评分与质量自检

## 定位

本技能是 `mathmodel-core` 主技能的**配套评审件**，只管「论文能不能交付、差在哪、扣几分」：

- **章节结构自检**：按 [`docs/chapter-checklist.md`](docs/chapter-checklist.md) 逐章核对（摘要三段式、问题重述/分析、假设编号、符号说明三线表、模型建立与求解链条、模型评价优缺点、参考文献、附录源程序、AI 使用声明、匿名与篇幅），可判定项由 `code/check_chapters.py` 自动执行——整理自《优秀论文自检表》与全国大学生数学建模竞赛论文格式规范（2026 年修订稿），契约在 `code/chapter-checklist.json`。
- **整体质量自检**：按 [`docs/self-check.md`](docs/self-check.md) 逐项核对（致命 / 严重 / 中等 / 轻微四级）。
- **评分**：按 [`docs/rubric.md`](docs/rubric.md) 的百分制五维口径打分；结构 hard 项未过不可进入评分。`code/score_card.py` 校验评分卡并渲染评分表，给出达标判定与优化轮次。
- 不管：赛题分析、算法选择、代码实现、正文写作、版式排版、去 AI 与字符清理——分别以主技能 `mathmodel-core`、`mathmodel-paper`、`mathmodel-deai` 为准。
- **表述口径以 `mathmodel-deai` 为准**：模板腔/套话/句式与段落节奏/零宽字符的判定权在该技能，本技能只引用其退出码与报告折算扣分；已知协调见 `docs/rubric.md`「与去 AI 模块的分工」（编号分点不计入句式与段落统计；统一格式指信息结构而非字数齐平）。
- **规范条文以本技能 `docs/` 为唯一权威出处**；主技能只保留强制项摘要并指向本文件，避免两处规范漂移。

## 评分标准

| 维度 (id) | 满分 | 评分依据 |
|---|---|---|
| 摘要 (`abstract`) | 30 | 结构完整性、数值具体性、递进关系、与正文一致性 |
| 算法/模型正确性 (`model`) | 20 | 数学推导无误、约束完备、求解结果合理 |
| 创新性 (`innovation`) | 20 | 方法创新度、跨学科融合、指标构建独创性 |
| 写作能力 (`writing`) | 15 | 逻辑连贯、学术语态、数据支撑、无空泛表达 |
| 排版 (`layout`) | 15 | 格式规范、图表完整、符号一致、编译无误 |
| **合计** | **100** | **$S \geq 85$ 方可最终输出** |

- **结构门槛**：章节结构 hard 项未过（缺符号说明、缺模型评价优缺点、附录缺源程序、正文含目录、出现身份信息等）先补齐，**不进入评分**
- **一票否决**：出现参赛者身份/学校/赛区信息或页眉等红线，直接淘汰、不计分，不进入优化循环
- **熔断**：最大优化轮次 **3 轮**；3 轮后仍未达标即输出当前版本并标注"未达 85 分标准，需人工复核"
- 扣分项与自检项一一对应；同一缺陷不在两个维度重复扣分（细则见 `docs/rubric.md`）
- **两赛口径**：国赛以「假设合理性、建模创造性、结果正确性、表述清晰性」为主，格式规范为硬约束；美赛不设分值表、第一轮只读摘要，看重问题驱动与思考痕迹（见 `docs/rubric.md` 末节）

## 快速流程

1. **章节结构门槛**（先跑，hard 未过先补齐再往下）：

   ```bash
   python3 code/check_chapters.py paper/paper.tex              # 默认国赛口径；0 通过 / 1 有未过项 / 2 用法错误
   python3 code/check_chapters.py paper/paper.tex --rules mcm   # 美赛口径（放宽目录要求，按 25 页限制）
   python3 code/check_chapters.py --list-checks                 # 查看结构契约（hard/soft/人工）
   ```

   逐条判据见 [`docs/chapter-checklist.md`](docs/chapter-checklist.md)，数据契约在 `code/chapter-checklist.json`；判定前会自动剔除 LaTeX 注释与代码块。

2. **整体质量自检**：按 `docs/self-check.md` 的四级清单逐项核对，记录未过项；涉及零宽字符/去 AI 的部分调用对应专项技能的门禁命令。

3. **填评分卡**（每维度给分并写明扣分项，可含优化轮次）：

   ```json
   {
     "schema_version": "1.0",
     "paper": "第X题_赛题简称",
     "round": 1,
     "veto": false,
     "dimensions": [
       {"id": "abstract", "score": 26, "deductions": [
         {"item": "字数超出 800-1000 字范围", "penalty": 3, "note": "摘要 1120 字"}]},
       {"id": "model", "score": 18, "deductions": []},
       {"id": "innovation", "score": 15, "deductions": []},
       {"id": "writing", "score": 13, "deductions": []},
       {"id": "layout", "score": 14, "deductions": []}
     ]
   }
   ```

   完整示例见 [`examples/example-scorecard.json`](examples/example-scorecard.json)。

4. **校验并渲染评分表**：

   ```bash
   python3 code/score_card.py scorecard.json          # 退出码 0 达标 / 1 需优化 / 2 输入错误
   python3 code/score_card.py scorecard.json --json    # 机器可读输出（含 verdict 与扣分明细）
   python3 code/score_card.py --list-dimensions        # 查看维度契约（含满分）
   ```

   脚本只做校验、加权汇总与渲染，不替使用者判断扣分；扣分合计与 (满分-得分) 不一致时会在 stderr 给出提示。

5. **按判定优化**：`判定：需优化`（$S<85$ 或任一维度为 0）时，按扣分分值从高到低逐项修改后重新评分；超过 3 轮触发熔断。

## 评分卡契约

- 顶层字段：`schema_version`、`paper`、`round`（可选）、`veto`（布尔）
- `dimensions` 必须恰好覆盖五个维度 id，`score` 为 0 到该维度满分之间的数值，缺失/未知/越界/重复均为输入错误（退出码 2）
- `deductions[]` 每项含 `item`（检查项）、`penalty`（扣分）、`note`（说明）
- 机器可读契约：`score_card.py --list-dimensions --json`

## 目录结构

```
mathmodel-score/
├── SKILL.md                       # 本文件：定位 + 评分标准 + 快速流程 + 评分卡契约
├── README.md                      # 目录组织说明
├── code/
│   ├── chapter-checklist.json     # 章节结构与格式规范契约（hard/soft/人工，数据源）
│   ├── check_chapters.py          # 章节结构自检器（国赛/美赛口径，退出码 0/1/2）
│   └── score_card.py              # 评分卡校验与渲染（argparse 入口，退出码 0/1/2）
├── docs/
│   ├── rubric.md                  # 百分制评分细则（唯一权威）：权重、各维度扣分、结构门槛、两赛口径、优化与熔断
│   ├── chapter-checklist.md       # 章节结构自检清单（人读版，逐章逐条）
│   └── self-check.md              # 论文质量自检清单（交付前审计，四级）
└── examples/
    ├── example-scorecard.json     # 示例评分卡（达标，总分 86）
    ├── chapter-sample.tex         # 结构正例（hard 全过）
    └── chapter-missing-sample.tex # 结构反例（多项 hard 未过）
```

## 与其他技能的关系

| 技能 | 关系 |
|---|---|
| `mathmodel-core` | 主技能。阶段六「论文评分与优化」与「论文质量自检清单」已收敛到本技能，主技能保留强制项摘要并指向本文件 |
| `mathmodel-deai` | **表述与字符口径的唯一权威**：自检中的「全文无 AI 痕迹」「零宽/不可见字符」由该技能的 `check_phrasing.py` / `check_style.py` / `strip_invisible.py` 判定，本技能只引用其结果折算扣分；编号分点不计入其句式与段落统计，避免与本技能要求的「假设 X」分点互相误伤 |
| `mathmodel-paper` | 自检中的「PDF 与 Word 格式一致性」「三线表/页眉页码」对应其版式规范与 `word_postprocess.py` |
| `mathmodel-figure` / `mathmodel-diagram` | 自检中的图表编号、图题表题、配色可辨识性对应其出图规范 |
