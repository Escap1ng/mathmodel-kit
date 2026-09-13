# 更新日志

本项目的所有重要变更都记录在此文件。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

破坏性变更边界（`MAJOR`）：移除既有 CLI 参数、移除登记表中的字段、移除主题契约字段、
扩大内容契约或主题契约的必备字段集合。

## [Unreleased]

### 新增

- **建模方法库与选型技能 `mathmodel-methods`**：把主技能中的算法库、选型依据与实现范式拆分为独立技能，按问题族（评价/排序、优化、预测、分类聚类、微分方程、仿真、信号、前沿创新）组织
  - `docs/method-library.md`：方法清单唯一出处（问题族索引 + 九类方法 + 新增方法收录标准）
  - `docs/selection-guide.md`：选型流程、候选对比表模板、问题特征对照、按问题类型的验证方式、问题递进关系、常见误用
  - `docs/implementation-guide.md`：推荐库速查、GA/SA/0-1 规划与数据读取的最小可运行骨架、实现纪律与技能分工
  - 主技能 `mathmodel-core/SKILL.md` 的「算法库」与「代码实现规范」改为强制项摘要 + 指向新技能；「快速参考」的算法选择速查、算法实现速查与问题递进关系移入新技能，消除两处规范漂移
- 技能数 6 → 7：README 中英的徽章、技能表、仓库结构与文档地图，`CONTRIBUTING` 的技能数与单一事实源表，白皮书中英的定位段与架构图同步新增 `mathmodel-methods`

### 变更

- **主技能瘦身**：`mathmodel-core/SKILL.md` 由 772 行降至 296 行——论文写作规范、排版规范（LaTeX）、参考文献规范与 Word 后处理条文整体移入 `mathmodel-paper`，主技能只保留强制项摘要与链接
- **`mathmodel-paper` 升格为论文域技能「论文写作与排版」**：新增 `docs/writing-rules.md`（写作规范）、`docs/typesetting-rules.md`（排版规范，含 Word 后处理）、`docs/references.md`（参考文献规范）三份唯一权威文档；SKILL.md 改为定位 + 文档地图 + 快速流程 + 交付红线，页面设置表与匿名红线清单不再与主技能重复
- **新增技能注册表 `skills/manifest.json`**：登记每个技能的类型（core / knowledge / tool）、职责、入口、文档与协作口径（`open` / `maintainer`），作为技能清单的单一事实源
- **CI `manifest-consistency` 扩展**：新增注册表 ↔ `skills/` 目录 ↔ README 技能表 ↔ 徽章计数的交叉校验（技能名集合、入口文件、文档路径、README 技能表登记、kind / contribution 取值）
- **frontmatter 规范化**：`mathmodel-core` 的 `name` 去引号并补齐 `allowed-tools`，七个技能的 SKILL.md 统一为 `name` / `description` / `allowed-tools` 三字段
- **协作口径明确**：主技能 `mathmodel-core` 由维护者掌握（外部只提 Issue、不接受直接 PR），其余技能与根文档、CI 接受外部贡献；口径写入 `skills/manifest.json` 与 CONTRIBUTING
- **CLI 契约**：退出码统一为 0/1/2；`--lang {zh,en}` 明确为面向用户入口的可选参数（8 个入口已覆盖，`word_postprocess.py` 与 `strip_invisible.py` 暂未提供，属 Experimental）

### 文档

- `CONTRIBUTING.md` / `CONTRIBUTING_EN.md` 重构为四个可协作子模块（M1 文档与示例、M2 代码与模板、M3 测试与验证、M4 问题反馈与需求），每个子模块给出贡献标准、提交规范与审核流程；新增「协作接口与信息同步」（单一事实源清单、子模块交接、同步机制）与「贡献者角色与权限」（报告者 / 贡献者 / 评审者 / 维护者及权限边界）两节
- `README.md` / `README_EN.md` 的「扩展与贡献」改为四个子模块入口表，文档地图同步；各技能 README 的「扩展约定」统一指向 `CONTRIBUTING.md`，避免两处规则漂移
- 白皮书中英 §7 的贡献路径按四个子模块改写，并说明贡献等级（激励口径）与角色权限（权限口径）的分工
- 新增缺陷报告 Issue 表单 `.github/ISSUE_TEMPLATE/bug_report.yml`；PR 模板新增「所属子模块」声明与 Stable 契约改动确认项

## [1.2.0] - 2026-09-13

新增降 AI 与评分两个技能，把原先分散的「去 AI 化规范」「零宽/不可见字符清理」与「论文质量自检 + 百分制评分」收敛为两个独立模块。全部为向后兼容的能力新增：既有命令与产物路径不变。

### 新增

- **降 AI 技能 `mathmodel-deai`**：论文去 AI 化（词表级 + 结构级）与交付前不可见字符清理（字符级）三道关
  - `code/check_phrasing.py` + 词表 `code/phrasing-blacklist.json`：19 条用词/句式规则，中文 16 条（模板腔开头、过渡词滥用、连接词链堆砌、泛化升华、模板腔结果表述、无依据断言、含糊词、权威含糊、口语化主观、二元对照、冒号揭晓、伪洞察开场、虚假深刻收尾、空泛形容词、冗长连接、模板化目的句）+ 英文 3 条（`en-slop-word` / `en-slop-phrase` / `en-slop-pattern`，用于英文摘要与图注）；按 `max_per_document` 频次上限判定，跳过围栏代码块与行内代码跨度，退出码 0/1/2
  - `code/check_style.py`：结构级六项指标（过长被动句、句式重复、过渡词密度、长短句比例、相邻段落节奏、结果小数位）并给出 AI 痕迹风险等级（低/中/高/极高）；统计类指标在样本过小时自动跳过，列表与表格行不计入
  - `docs/deai-rules.md`：降 AI 规范唯一权威出处（痕迹清单、改写规则、负面清单、个性化表述规范、摘要去模板化对照表、结构级十项升级细则、修订痕迹与风险等级、三关门禁与扩词流程）
  - `docs/no-ai-slop-reference.md`：petergyang/no-ai-slop 英文 slop 模式清单的整理稿（MIT License，Copyright (c) 2026 Peter Yang，随文件保留上游版权声明与来源 commit）
  - `examples/slop-sample.tex` / `examples/slop-sample-en.md`（词表级反例）、`examples/style-slop-sample.tex`（结构级反例）与 `examples/clean-sample.tex` / `examples/clean-sample-en.md`（正例）
- CI 新增 `deai-phrasing` job：中英两套词表反例分别必须退出 1、正例必须退出 0，结构级反例必须退出 1，技能自身文档须通过词表级门禁
- **评分技能 `mathmodel-score`**：论文交付前自检 + 百分制五维评分（摘要 30 / 算法模型 20 / 创新性 20 / 写作 15 / 排版 15）
  - `code/score_card.py`：评分卡校验与评分表渲染（加权汇总、达标判定 ≥85、一票否决、熔断 3 轮提示），`--list-dimensions` 提供维度契约，退出码 0 达标 / 1 需优化 / 2 输入错误
  - `docs/rubric.md`：百分制评分细则唯一权威出处（五维权重、各维度扣分标准、结构门槛与 soft 项维度映射、国赛/美赛口径对照、优化触发与熔断、评分表模板）
  - `docs/chapter-checklist.md` + `code/chapter-checklist.json` + `code/check_chapters.py`：章节结构与格式规范自检（整理自《优秀论文自检表》与国赛论文格式规范 2026 修订稿），20 项检查分 hard（未过先补齐、不计分）/ soft（按维度扣分）/ 人工，支持 `--rules cumcm|mcm`，判定前剔除 LaTeX 注释与代码块，退出码 0/1/2
  - `docs/self-check.md`：论文质量自检清单（交付前审计，致命/严重/中等/轻微四级）
  - `examples/example-scorecard.json`（示例评分卡，总分 86）、`examples/chapter-sample.tex` / `examples/chapter-missing-sample.tex`（结构正/反例）
- CI 新增 `scorecard` job：章节结构正例必须退出 0、反例必须退出 1；示例评分卡必须退出 0，低于达标线的评分卡必须退出 1，结构错误的输入必须退出 2

### 变更

- 主技能目录 `math-modeling-helper` 更名为 `mathmodel-core`（与 `mathmodel-figure` / `mathmodel-diagram` / `mathmodel-paper` / `mathmodel-deai` 前缀一致），SKILL.md 的 `name` 与全部文档/CI 引用同步更新；1.0.0 与 1.1.0 的历史条目保留当时的目录名
- `strip_invisible.py` 从 `mathmodel-paper` 迁移到 `mathmodel-deai`（保留 git 历史），字符集与 Layer A 保护逻辑不变
- 主技能 `mathmodel-core` 的「去 AI 化要求」「负面清单」「个性化表述规范」改为强制项摘要 + 指向 `mathmodel-deai/docs/deai-rules.md`（防双写漂移）；阶段五与自检清单中的清理命令改指向降 AI 技能
- `mathmodel-paper` 不再包含零宽字符清理，相关命令与目录登记改由 `mathmodel-deai` 承担
- CI `strip-invisible` job 的脚本路径更新为 `skills/mathmodel-deai/code/strip_invisible.py`
- 主技能 `mathmodel-core` 的「论文质量自检清单」与「最终论文评分（百分制）」两节收敛为「论文质量自检与评分」强制项摘要 + 指向 `mathmodel-score`，阶段六改为调用该技能
- 技能数 5 → 6；`mathmodel-paper`、`mathmodel-deai`、`mathmodel-figure` 文档中的自检与评分引用改指 `mathmodel-score`
- **口径统一（表述类以 `mathmodel-deai` 为准）**：评分模块不再自定表述判据，`docs/rubric.md` 增「与去 AI 模块的分工」，只引用去 AI 技能的退出码与报告折算扣分
- `check_style.py` 将列表项、编号分点（`假设 X`、`（1）`、`①`、`步骤 X`）与参考文献条目 `[1]` 排除在句式重复（M2）与段落节奏（M5）之外，消除与章节规范「假设 X 分点列出」的互相误伤
- 评分模块自身文档与中英 README 改为经去 AI **词表级**门禁校验（反例词改为行内代码）；结构级指标明确只面向论文稿（`.tex` 与论文类 `.md`），项目说明文档不套用行文节奏类指标。CI `deai-phrasing` job 新增跨模块步骤：项目文档过词表级、论文样例过结构级
- `check_style.py` 进一步排除清单块的换行续行与 README 类 HTML 区块，消除长文档的段落节奏误报

### 文档

- README 中英：技能表新增 `mathmodel-deai` 与 `mathmodel-score`，技能数与徽章 4 → 6，快速开始补第 5、6 步，质量门禁表补「表述级去 AI 检查」并更新「自评分卡」，仓库结构与文档地图同步并补致谢
- 白皮书中英、`CONTRIBUTING.md` / `CONTRIBUTING_EN.md` 的技能数量表述同步为六个技能

### 来源与致谢

- 句式规则分类参考 [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop)
- 字符集与保护逻辑（Layer A）来自 [guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover)

## [1.1.0] - 2026-09-01

面向「开放、可合作的数模工具箱」的首批基础设施。全部为向后兼容的能力新增：既有命令与产物路径不变。

### 新增

- **模板注册表（机器可读的单一事实源）**
  - `skills/mathmodel-figure/code/tools/manifest.json`：20 个数据图表模板（id、脚本、分组、别名、中文提示、预览、署名）
  - `skills/mathmodel-diagram/code/templates/manifest.json`：5 个示意图模板（含内容契约、示例、预览、说明文档索引）
- **内容契约与校验器**：`skills/mathmodel-diagram/code/templates/schema/*.schema.json` 五份 JSON Schema（Draft 2020-12）
  覆盖五个示意图模板的输入结构；`code/tools/validate_content.py` 提供单文件、`--all`、`--schemas` 三种校验模式，
  退出码 0/1/2 与 `strip_invisible.py` 语义一致，未安装 `jsonschema` 时降级为内置最小校验器
- **示意图统一入口** `skills/mathmodel-diagram/code/tools/render_template.py`：`--list`、`--list --json`、
  `--check`、`-o/--out`，支持 id / 英文别名 / 中文片段三级解析
- **配色主题契约**：`skills/mathmodel-figure/themes/theme.schema.json` 把配色规则（身份 / 基准 / 方向 / 层级
  四类角色）变成可声明、可替换、可校验的数据，默认主题 `themes/nature.theme.json`；
  `code/tools/validate_theme.py` 提供单文件、`--all`、`--list` 三种模式，
  校验结构合法性、色值格式、文件名与 `name` 一致性、同目录重名
- **数据图表渲染器新增 `--theme <主题名|路径>` 与 `--list-themes`**：渲染时把所选主题写入工作区
  `scripts/theme.json`，工作区因此自包含（脚本与主题一起交付，重跑得到同一套颜色），改这份副本即可覆盖配色
- **协作与治理**：`CONTRIBUTING.md`、`CONTRIBUTING_EN.md`、PR 模板、新增模板需求 Issue 表单
- **版本治理**：`VERSION`、本文件、`.github/workflows/release.yml`（tag `v*` 触发，校验 tag 与 `VERSION` 及
  本文件一致性后生成 Release notes）

### 变更

- 数据图表渲染器的模板注册表由脚本内硬编码字典改为读取 `manifest.json`；`--list` 输出与解析行为保持不变
- 数据图表渲染器与示意图统一入口新增 `--lang {zh,en}`（默认 `zh`）：控制默认输出目录名与消息语言
- `skills/mathmodel-paper/templates/paper.tex` 的西文字体改为带回退的探测：优先 `Times New Roman`，
  缺失时自动回退到度量兼容的 `TeX Gyre Termes`，CI 不再需要打补丁
- CI `figures` / `diagrams` job 的模板数量与清单断言改为由注册表派生，新增 `manifest-consistency` job
  （登记表 ↔ 文件系统 ↔ 索引文档 ↔ 版本号 ↔ README 徽章 互相校验）
- `skills/mathmodel-figure/code/style/plot_style.py` 的颜色常量改为从主题文件展开
  （同目录 `theme.json` → 内置默认主题 → 内置兜底）：常量名与类型不变，默认主题下取值与升级前逐值一致
- CI 新增主题契约校验步骤、工作区主题落盘断言与主题覆盖冒烟；`manifest-consistency` 追加默认主题存在性校验

### 修复

- `validate_content.py` 读取内容文件时改用 `utf-8-sig`，容忍 Windows 编辑器写入的 BOM

### 文档

- 新增升级白皮书 `docs/upgrade-plan.md` / `docs/upgrade-plan_EN.md`（可行性、挑战、模块化架构、
  数据模型标准化、开放接口、合作与激励、版本策略、竞争优势、实施路径与成果评估标准）
- 新增模板的交付清单收敛为「注册表加一行 + 索引文档加一行」，不再需要改动 CLI、CI 与版本号
- 修正「配色只改 `plot_style.py`，20 个模板一并生效」的表述：主题控制覆盖共用样式模块的 9 个图表模板
  与自绘图，其余 11 个模板与 5 个示意图的配色写在其脚本头部（README 中英、`mathmodel-figure/SKILL.md`、
  白皮书均已按实测口径改写）
- README 中英按开源项目惯例重构：首屏写清「是什么、给谁用」，新增可复制的「30 秒上手」与「文档地图」索引，
  徽章收敛到只保留真信号（构建状态、许可证、版本、能力计数、参与入口），并新增「定位与合规声明」一节
- 「开放设计」新增「未来会更开放」时间表：写明现在已落地什么、Phase 2/3 会开放到什么程度及其触发条件

## [1.0.0] - 2026-08-29

首个发布版本，确立四个技能的分工与质量门禁。

### 新增

- `math-modeling-helper`（主技能）：赛题分析 → 模型构建 → 算法实现 → 论文输出 → 评分优化的六阶段编排，
  附代码规范、论文写作规范、自检清单与百分制评分细则
- `mathmodel-figure`：20 个 matplotlib 数据图表模板 + 模板库外的 Nature 出图标准
- `mathmodel-diagram`：5 个 JSON 驱动的学术示意图模板，另支持从零手写与参考图高保真复刻
- `mathmodel-paper`：LaTeX 骨架 → PDF → Word 流水线，含竞赛版式微调与零宽/不可见 Unicode 字符清理
- CI（语法、模板渲染冒烟、零宽字符清理冒烟）与论文 LaTeX 编译验证
