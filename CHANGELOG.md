# 更新日志

本项目的所有重要变更都记录在此文件。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

破坏性变更边界（`MAJOR`）：移除既有 CLI 参数、移除登记表中的字段、移除主题契约字段、
扩大内容契约或主题契约的必备字段集合。

## [Unreleased]

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
