# 贡献指南

感谢愿意为 `mathmodel-kit` 出一份力。本项目的目标是把数学建模里**机械正确**的部分（图表、流程示意、排版、交付校验）
做成确定性、可复现、可校验的组件，把**建模判断**留给使用者。贡献也围绕这条线展开。

> English version: [CONTRIBUTING_EN.md](CONTRIBUTING_EN.md)

---

**目录**：[协作总览](#一协作总览) · [先明确什么适合做成模板](#二先明确什么适合做成模板) · [协作子模块](#三协作子模块) · [协作接口与信息同步](#四协作接口与信息同步) · [环境目录与代码风格](#五环境目录与代码风格) · [贡献者角色与权限](#六贡献者角色与权限) · [提交与-pr](#七提交与-pr) · [评审口径](#八评审口径) · [署名与许可](#九署名与许可) · [行为准则](#十行为准则)

---

## 一、协作总览

可协作的事收敛成四个子模块。每个子模块按**贡献标准 → 提交规范 → 审核流程**三段式写清（第三节）；
跨模块的交接与同步规则在第四节，角色与权限在第六节。

| 子模块 | 管什么 | 主要交付物 | 事实源 | 审核方 |
|---|---|---|---|---|
| **M1 文档与示例** | 规范条文、方法指南、逐模板说明、示例与预览 | `docs/**`、`SKILL.md`、`README.md`、示例文件 | 对应技能的规范文件 | 评审者 |
| **M2 代码与模板** | 模板脚本、工具、注册表与契约 | `code/templates/**`、`code/tools/**`、`manifest.json`、`*.schema.json` | 注册表（单一事实源） | 评审者 |
| **M3 测试与验证** | 本地自测、CI 门禁、契约校验 | 验证命令与输出、CI 全绿记录 | `.github/workflows/ci.yml` 与各校验器 | CI + 评审者 |
| **M4 问题反馈与需求** | 缺陷报告、模板需求、文档纠错 | Issue（最小复现或需求表单） | Issue 表单 | 评审者 / 维护者分流 |

四个子模块的产出最终汇入同一条链：**注册表是单一事实源 → CI 校验一致性 → 人只审机器判不了的部分**。

**协作范围**：主技能 `mathmodel-core` 由维护者掌握（外部只提 Issue 反馈，不接受直接 PR）；其余技能与根文档、CI 接受外部贡献。
范围以 [`skills/manifest.json`](skills/manifest.json) 的 `contribution` 字段为准，技能清单与类型（core / knowledge / tool）也登记在该文件。

---

## 二、先明确什么适合做成模板

**一次性图型不要做模板**——直接按 `skills/mathmodel-diagram/docs/guides/authoring.md` 或
`skills/mathmodel-figure/docs/guides/nature-standard.md` 手写更快。

只有「某类图会反复画」时才值得进模板库。判断标准：换一批数据/文案后，图的**结构**仍然成立。

---

## 三、协作子模块

### M1 文档与示例

**贡献标准**

- 规范条文只留一处权威，其余文档写强制项摘要并链接过去，不在两处复述同一条规则；
- 示例填满真实内容，不用占位符；示意图的逐模板说明必须给出逐槽**实测**汉字预算与语义约定（并列/汇流/对比）；
- 数字、结论与引用必须能追溯到仓库内可复现的产物或可核实来源，禁止编造数据与文献；
- 术语与命名沿用既有约定：模板 id 用 kebab-case、脚本名用 snake_case、路径相对注册表所在目录。

**提交规范**

- 提交信息用 `docs(<scope>): <中文摘要>`；
- 改动索引表（`figure-catalog.md`、示意图 `SKILL.md` 的模板索引表）时，与对应的注册表改动放进同一个 PR；
- 规范类文档要能通过词表级去 AI 检查（`python3 code/check_phrasing.py <文档>`）；项目说明文档不套用行文节奏类指标。

**审核流程**

- 人只审机器判不了的部分：语义是否正确、文案是否忠于来源、预算是否实测、是否值得写进文档；
- 只改文档也走 PR，由评审者审后合并；索引表与注册表缺一即退回。

### M2 代码与模板

**贡献标准**

- 代码风格见第五节；模板必须自带确定性数据或由 content JSON 驱动，禁止把文案写进脚本；
- 新增模板服从注册表契约：字段、路径解析、产物格式与命名都按既有条目填写，不新造字段；
- 只改观感而破坏既有调用契约（CLI 参数、注册表字段、产物路径）的改动会被拒收。

**提交规范**

- 提交信息用 `<type>(<scope>): <中文摘要>`，`type` 取 `feat` / `fix` / `refactor` / `chore`；
- 新增模板按「注册表一行 + 索引文档一行」落盘（交接清单见 4.2），CLI、CI 与版本号无需改动；
- 不提交生成物：工作区目录、`.aux`、PDF/PNG 产物等（见 `.gitignore`）。

**审核流程**

- CI 全绿是前置条件（见 M3）；人工评审只看语义、原创性与契约稳定性；
- 涉及 Stable 契约（CLI 参数与退出码、注册表字段、主题契约字段）的改动由维护者决策，破坏性变更须升 `MAJOR` 并记入 `CHANGELOG.md`。

#### M2.1 数据图表模板（`mathmodel-figure`）

1. 写脚本 `skills/mathmodel-figure/code/templates/make_<name>.py`
   - 自带**种子化**模拟数据（`np.random.default_rng(<固定种子>)`），保证可复现；
   - 需要统一配色时 `from plot_style import ...`（渲染器会自动把 `plot_style.py` 一并复制到工作区）；
   - 产物一律 PNG（300 DPI）+ PDF + SVG，文件名 `<name>_replica.*`；
2. 加注册表一项：`skills/mathmodel-figure/code/tools/manifest.json` 的 `templates` 数组
   （字段见同文件既有条目：`id`、`script`、`title`、`group`、`aliases`、`cjk_hints`、`preview`、`author`）；
3. 放预览图 `skills/mathmodel-figure/examples/previews/<name>_replica.png`；
4. 在 `skills/mathmodel-figure/docs/templates/figure-catalog.md` 的目录表加一行。

#### M2.2 学术示意图模板（`mathmodel-diagram`）

1. 写脚本 `skills/mathmodel-diagram/code/templates/<id>.py`（`id` 用 kebab-case，脚本名用 snake_case）
   - 一律基于 `code/common.py` 的基元层（`Recorder` + `draw_*` + `guard` + `save_figure`）；
   - CLI 固定：`<脚本> content.json -o out.png` 与 `<脚本> content.json --check`；
   - **写文件前逐槽做中文字宽校验**，超框报出槽位与预算并以非零码退出；
   - 几何常量集中在文件头，内容一律来自 JSON，禁止把文案写进脚本；
2. 写内容契约 `skills/mathmodel-diagram/code/templates/schema/<id>.schema.json`（JSON Schema Draft 2020-12）
   - **必备字段以代码事实为准**：只有 `need()` 调用或 `c['key']` 下标访问的字段才是必备，其余走 `.get()` 的为可选；
   - 保留 `additionalProperties: true`，允许 `_comment` 等元信息；
3. 加注册表一项：`skills/mathmodel-diagram/code/templates/manifest.json`（含 `schema`、`example`、`preview`、`doc` 路径）；
4. 放示例 `examples/<id>/example.json`（**填满真实内容，不要占位符**）与预览 `examples/<id>/preview.png`；
5. 写说明 `docs/templates/<id>.md`：必须包含每个字段的**汉字预算**（用脚本算，不要手估）、数量允许区间、
   以及「哪些槽位是并列/汇流/对比」的语义约定；
6. 在 `skills/mathmodel-diagram/SKILL.md` 的模板索引表加一行。

> 关于标定方法、matplotlib 画法的四个坑、复刻与自检流程，见
> `skills/mathmodel-diagram/docs/templates/adding-templates.md`。

**你不需要改 CLI、CI 与版本号**——注册表是单一事实源，其余一致性由 CI 自动校验。

### M3 测试与验证

**贡献标准**

- 提交前在本地把能跑的门禁跑一遍；新增或修改的模板必须实际渲染出非空产物，不接受「应该能跑」；
- 统一退出码语义：`0` 成功 / `1` 校验或渲染失败 / `2` 用法或环境错误；
- 变更涉及契约时（Schema、注册表、词表、评分维度），同步更新示例与期望结果。

**提交规范**

- PR 的「验证」栏贴出**实际执行过的命令与关键输出**，不是计划清单；
- 只给结论、不给命令的 PR 会被要求补证据；
- 本地验证通过与否都不替代 CI；CI 是合并的硬门槛。

**审核流程**

- 合并前 CI 必须全绿，覆盖：

| 检查 | 内容 |
|---|---|
| `syntax` | 全部 Python 脚本可编译 |
| `manifest-consistency` | 注册表 ↔ 文件系统 ↔ 索引文档 ↔ 版本号 ↔ README 徽章 互相一致；JSON Schema 合法且内置示例通过严格校验 |
| `figures` / `diagrams` | 每个模板都能渲染出非空产物 |
| `strip-invisible` | 零宽字符清理器往返行为正常 |
| `deai-phrasing` / `scorecard` | 去 AI 门禁与评分卡的冒烟用例按预期退出码通过 |
| `Paper LaTeX build` | 论文骨架可编译 |

- 机器能判定的（语法、一致性、Schema、渲染成功、退出码）不再进入人工评审，人只处理 CI 判不了的语义与原创性。

### M4 问题反馈与需求

**贡献标准**

- 缺陷报告给**最小复现**：内容 JSON（或脚本片段）+ 命令 + 实际输出 + 期望输出，能附退出码就附；
- 模板需求先回答两个问题：这张图会不会反复出现、现有 25 个模板里有没有可直接复用的；
- 文档纠错直接指出章节与原文，改法可一并给出。

**提交规范**

- 用对应的 Issue 表单提交（缺陷报告 / 新增模板需求），标题前缀沿用表单默认值；
- 拿不准要不要做时先开 Issue 讨论，不要直接写代码；
- Issue 里不要贴赛题原文之外的敏感信息或个人身份信息。

**审核流程**

- 评审者 / 维护者认领后给 Issue 打标签，判定归属子模块，需要时转交 M1 或 M2，并在 Issue 里说明下一步；
- 不接受的（一次性图型、越界改造等）要给出理由与替代做法（例如「按 `nature-standard.md` 现绘即可」）；
- 被采纳并合并的贡献记入 `CHANGELOG.md`，发版时进入 Release notes。

---

## 四、协作接口与信息同步

### 4.1 单一事实源

同一事实只在一处维护，其余位置读它、或在 CI 里对齐：

| 事实 | 唯一来源 | 谁读它 | 谁维护 |
|---|---|---|---|
| 技能清单、类型与协作口径 | `skills/manifest.json` | CI、README 技能表、贡献者 | 维护者 |
| 图表模板清单与字段 | `skills/mathmodel-figure/code/tools/manifest.json` | 渲染器、CI、索引文档 | M2 |
| 示意图模板清单与字段 | `skills/mathmodel-diagram/code/templates/manifest.json` | 统一入口、CI、`SKILL.md` | M2 |
| 示意图输入结构 | `code/templates/schema/*.schema.json` | 校验器、模板脚本 | M2 |
| 配色契约 | `themes/theme.schema.json` + `themes/*.theme.json` | `plot_style.py`、渲染器、CI | M2 |
| 去 AI 词表 | `skills/mathmodel-deai/code/phrasing-blacklist.json` | 检查器、规范文档 | M1 / M2 |
| 建模方法与选型 | `skills/mathmodel-methods/docs/method-library.md` | 主技能、其他技能、使用者 | M1 |
| 章节结构契约 | `skills/mathmodel-score/code/chapter-checklist.json` | 检查器、人读清单 | M2 |
| 版本号 | 根 `VERSION` | CI、`release.yml`、`CHANGELOG.md` | 维护者 |
| 变更历史 | `CHANGELOG.md` | 用户、Release notes | 维护者 |

### 4.2 子模块之间的交接

- **M4 → M1 / M2**：Issue 定性后，把最小复现或需求描述作为输入交给对应子模块；PR 用 `Closes #<issue>` 建立回溯。
- **M2 → M1**：新增或改动模板时，注册表、索引文档、逐模板说明、预览图四处在同一次 PR 内更新，缺一处即被 CI 或人工退回。
- **M2 → M3**：代码改动必须附本地验证命令与输出；CI 通过是合并的前置条件。
- **M1 → M3**：文档改动须通过词表级检查；改写规范条文后复查权威文件与摘要是否还一致。
- **M3 → 全部**：CI 是对齐机制，机器能判定的部分不进入人工评审。

### 4.3 信息同步机制

- **注册表一致性**：每次 push / PR 由 CI 校验注册表 ↔ 文件系统 ↔ 索引文档 ↔ 版本号 ↔ README 徽章五处一致；
- **版本三处一致**：`VERSION` == 发布标签 == `CHANGELOG` 小节，由 `release.yml` 强校验；
- **契约不双写**：规范条文只留一处权威，其余文档只做强制项摘要 + 链接（主技能与专项技能即按此分工）；
- **变更可见**：每次合并补 `CHANGELOG.md` 对应小节，发版自动从 CHANGELOG 生成 Release notes。

---

## 五、环境、目录与代码风格

### 5.1 开发环境

- Python 3.12 及以上（CI 以 3.12 为最低验证版本）
- 数据图表：`pip install matplotlib numpy seaborn`
- 示意图：`pip install matplotlib numpy`
- 契约校验：`pip install jsonschema`（可选；未安装时校验器会降级为内置最小校验器）
- 论文链路：`xelatex`、`pandoc`，Word 后处理需 `python-docx`

提交前请在本地跑一遍：

```bash
python -m compileall -q skills
```

### 5.2 目录约定

七个技能各自自包含，**不要把文件放到技能目录之外**（`docs/` 只放对外方案文档）：

```
skills/<skill>/
├── SKILL.md            # 技能契约：何时用、怎么用、边界在哪
├── code/               # 可执行脚本（templates/ 放模板，tools/ 放入口与校验器）
├── docs/               # 人读说明（guides/ 方法，templates/ 逐模板说明）
└── examples/           # 示例与预览图
```

技能分三类（见 `skills/manifest.json`）：**core**（只有 `SKILL.md`）、**knowledge**（`SKILL.md` + `docs/`）、
**tool**（`code/` + `docs/` + `examples/`）。新增技能要先在注册表登记，CI 校验注册表 ↔ 目录 ↔ README 技能表 ↔ 徽章计数一致。

### 5.3 代码风格

- Python：4 空格缩进，标准库优先；脚本用 `argparse`，参数风格对齐既有脚本
  （`-o/--out`、`--check`、`--list`、`--lang`）；
- **退出码语义**：`0` 成功 / `1` 校验或渲染失败 / `2` 用法或环境错误；
- **CLI 契约**：退出码全量统一；`--lang {zh,en}` 是面向用户入口的可选参数（8 个入口已覆盖，`word_postprocess.py`
  与 `strip_invisible.py` 暂未提供，属 Experimental，补齐不视为破坏性变更）；
- 注释与文档字符串用中文（与仓库一致），面向用户的消息提供 `--lang {zh,en}` 时中英并行；
- 不引入新的格式化/检查工具链（仓库不依赖 ruff/black/pytest）；
- 不提交生成物（工作区目录、`.aux`、PDF/PNG 产物等，见 `.gitignore`）。

---

## 六、贡献者角色与权限

角色按实际贡献累积，权限与责任对等。这里的**角色**是权限维度，与白皮书 §8 的贡献等级 L1–L4 是两套口径。

| 角色 | 谁能担任 | 权限 | 可见回报 |
|---|---|---|---|
| **报告者** | 任何人 | 提交 Issue（缺陷 / 需求） | 被采纳的反馈记入 `CHANGELOG.md` 与 Release notes |
| **贡献者** | 提交过被合并的 PR | 提 PR（文档、示例、代码、模板） | 模板作者在注册表 `author` 字段永久署名 |
| **评审者** | 持续评审并获维护者邀请 | 评审 PR、给出结论、请求修改 | 评审记录计入 `CHANGELOG.md` |
| **维护者** | 长期参与并熟悉规则 | 合并、发版、改 CI 与版本号、决策 Stable 契约变更 | 列为白皮书路线图中的共同维护者 |

**权限边界**（对应「开放设计」的接口分级）：

| 改动对象 | 谁可以决定 | 说明 |
|---|---|---|
| 文档、示例、词表加词、模板与脚本 | 贡献者提 PR，评审者审核 | 常规路径 |
| 注册表字段语义、内容契约必备字段、主题契约字段、CLI 参数与退出码 | 维护者 | 属 Stable 契约，破坏性变更须升 `MAJOR` 并记入 `CHANGELOG.md` |
| `VERSION`、`CHANGELOG` 小节、CI 工作流、发版 | 维护者 | 发版由标签触发，三处一致性由 `release.yml` 校验 |
| Issue 分流与标签 | 评审者 / 维护者 | 判定归属子模块并推进 |

责任约定：评审者只对机器判不了的部分负责（语义、忠于来源、预算实测、是否值得）；维护者负责契约稳定与版本治理，不以个人偏好替代可复现证据。

---

## 七、提交与 PR

提交信息沿用仓库既有风格：`<type>(<scope>): <中文摘要>`，`type` 取
`feat` / `fix` / `docs` / `refactor` / `chore`，正文说明**为什么**改（而非复述改了什么）。

PR 请使用仓库的 PR 模板，逐项确认，并声明所属子模块（M1 文档与示例 / M2 代码与模板 / M3 测试与验证）。
CI 必须全绿，门禁清单见 M3 一节。

---

## 八、评审口径

机器能判定的（语法、一致性、Schema、渲染成功）交给 CI，**人只评审机器判不了的**：

- 槽位**语义**是否正确（并列/汇流/对比放错，比字数超框严重得多）；
- 文案是否忠于来源材料（**禁止编造数据与文献**）；
- 字数预算是否**实测**得出（不接受手估）；
- 是否值得做成模板。

拒收情形：编造数据或文献；语义标注错误；只改观感却破坏既有调用契约（CLI 参数、注册表字段、产物路径）。

---

## 九、署名与许可

本项目以 [Apache-2.0](LICENSE) 分发，贡献即表示同意以同一许可发布。

模板作者会在对应注册表的 `author` 字段**永久署名**，并在模板目录中与官方模板并列展示；
修复与文档贡献会记入 [CHANGELOG.md](CHANGELOG.md) 并在 Release notes 中致谢。

---

## 十、行为准则

就事论事，对事不对人；技术分歧以**可复现的证据**为准（命令、输入、输出），而不是以资历或篇幅为准。
不接受任何形式的抄袭、数据伪造与文献编造。
