# mathmodel-score

论文评分与质量自检模块：按百分制五维对论文打分，交付前逐项自检并输出评分表与达标判定。入口文件是 [SKILL.md](SKILL.md)，评分口径以 [docs/rubric.md](docs/rubric.md) 为唯一权威、自检依据以 [docs/self-check.md](docs/self-check.md) 为准；本 README 只说明目录组织，与其余技能采用同一套分类规范。

## 目录结构

```
mathmodel-score/
├── SKILL.md                       # 技能入口：定位、评分标准、快速流程、评分卡契约、与其他技能的关系
├── README.md                      # 本文件：结构说明
├── code/                          # 可执行脚本与数据契约
│   ├── chapter-checklist.json     #   章节结构与格式规范契约（hard/soft/人工，唯一数据源）
│   ├── check_chapters.py          #   章节结构自检：国赛/美赛口径，hard 未过即退出 1
│   └── score_card.py              #   评分卡校验与渲染：加权汇总 + 达标判定 + 评分表（退出码 0/1/2）
├── docs/                          # 规范
│   ├── rubric.md                  #   百分制评分细则（唯一权威）：五维权重、各维度扣分、结构门槛、两赛口径、优化与熔断
│   ├── chapter-checklist.md       #   章节结构自检清单（人读版）：摘要/问题重述/分析/假设/符号/建模/评价/附录/参考文献/匿名
│   └── self-check.md              #   论文质量自检清单（交付前审计）：致命/严重/中等/轻微四级
└── examples/                      # 可复现示例
    ├── example-scorecard.json     #   示例评分卡（总分 86，达标）
    ├── chapter-sample.tex         #   结构正例（hard 全过，供 check_chapters 冒烟）
    └── chapter-missing-sample.tex #   结构反例（多项 hard 未过）
```

## 分类依据

- **一级按内容类型分**（`code/` `docs/` `examples/`）：与 `mathmodel-figure`、`mathmodel-diagram`、`mathmodel-paper`、`mathmodel-deai` 共用同一份目录词表，跨技能检索时语义不变——`code/` 恒为「可执行脚本与数据契约」、`docs/` 恒为「规范」、`examples/` 恒为「可复现示例」。
- **两套契约都是数据**：评分卡 JSON（维度与扣分）与章节结构契约 `code/chapter-checklist.json`（hard/soft/人工）都可被第三方程序读取；脚本只做校验、汇总与渲染，不替使用者判断。
- **口径单一来源**：五维权重与扣分细则只在 `docs/rubric.md`；章节结构判据只在 `code/chapter-checklist.json`（人读版 `docs/chapter-checklist.md`）；整体质量四级清单只在 `docs/self-check.md`。主技能 `mathmodel-core` 只保留强制项摘要。
- **口径有出处**：章节契约整理自《优秀论文自检表》与全国大学生数学建模竞赛论文格式规范（2026 年修订稿）；两赛评阅侧重对照见 `docs/rubric.md` 末节（附官方与评委经验链接）。
- **规范条文不在此仓库复制**：建模、写作、排版、去 AI 的条文分别留在 `mathmodel-core` / `mathmodel-paper` / `mathmodel-deai`，本技能只承接「结构自检 + 评分」这一类。
- **层级最深 2 层**。

## 扩展约定

新增维度、调整权重/扣分项，或增删章节结构自检项的交付清单：

```
code/score_card.py                 # DIMENSIONS 常量（id/label/max）与 PASS_SCORE、MAX_ROUNDS
code/chapter-checklist.json        # 章节结构契约（唯一数据源，check_chapters.py 读取）
docs/rubric.md                     # 同步权重表与扣分细则（唯一权威）
docs/chapter-checklist.md          # 同步人读版清单（与 JSON 逐条对应）
examples/example-scorecard.json    # 同步示例评分卡（保持达标且扣分合计自洽）
examples/chapter-sample.tex        # 结构正例须保持 hard 全过；反例须保持 hard 未过
```

约定：

- 维度 `id` 与自检项 `id` 都是机器契约的一部分，改动即为破坏性变更，须记入 `CHANGELOG.md`。
- 脚本一律提供 `argparse` 入口，退出码统一为 `0` 通过 / `1` 有未过项 / `2` 用法或输入错误。
- 扣分项与 `docs/self-check.md` 的自检项保持一一对应，避免两处口径漂移。
