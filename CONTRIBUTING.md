# 贡献指南

感谢愿意为 `mathmodel-kit` 出一份力。本项目的目标是把数学建模里**机械正确**的部分（图表、流程示意、排版、交付校验）
做成确定性、可复现、可校验的组件，把**建模判断**留给使用者。贡献也围绕这条线展开。

> English version: [CONTRIBUTING_EN.md](CONTRIBUTING_EN.md)

---

## 一、先明确什么适合做成模板

**一次性图型不要做模板**——直接按 `skills/mathmodel-diagram/docs/guides/authoring.md` 或
`skills/mathmodel-figure/docs/guides/nature-standard.md` 手写更快。

只有「某类图会反复画」时才值得进模板库。判断标准：换一批数据/文案后，图的**结构**仍然成立。

---

## 二、开发环境

- Python 3.12 及以上（CI 以 3.12 为最低验证版本）
- 数据图表：`pip install matplotlib numpy seaborn`
- 示意图：`pip install matplotlib numpy`
- 契约校验：`pip install jsonschema`（可选；未安装时校验器会降级为内置最小校验器）
- 论文链路：`xelatex`、`pandoc`，Word 后处理需 `python-docx`

提交前请在本地跑一遍：

```bash
python -m compileall -q skills
```

---

## 三、目录约定

四个技能各自自包含，**不要把文件放到技能目录之外**（`docs/` 只放对外方案文档）：

```
skills/<skill>/
├── SKILL.md            # 技能契约：何时用、怎么用、边界在哪
├── code/               # 可执行脚本（templates/ 放模板，tools/ 放入口与校验器）
├── docs/               # 人读说明（guides/ 方法，templates/ 逐模板说明）
└── examples/           # 示例与预览图
```

---

## 四、如何新增一个模板（最常见贡献）

### 4.1 数据图表模板（`mathmodel-figure`）

1. 写脚本 `skills/mathmodel-figure/code/templates/make_<name>.py`
   - 自带**种子化**模拟数据（`np.random.default_rng(<固定种子>)`），保证可复现；
   - 需要统一配色时 `from plot_style import ...`（渲染器会自动把 `plot_style.py` 一并复制到工作区）；
   - 产物一律 PNG（300 DPI）+ PDF + SVG，文件名 `<name>_replica.*`；
2. 加注册表一项：`skills/mathmodel-figure/code/tools/manifest.json` 的 `templates` 数组
   （字段见同文件既有条目：`id`、`script`、`title`、`group`、`aliases`、`cjk_hints`、`preview`、`author`）；
3. 放预览图 `skills/mathmodel-figure/examples/previews/<name>_replica.png`；
4. 在 `skills/mathmodel-figure/docs/templates/figure-catalog.md` 的目录表加一行。

### 4.2 学术示意图模板（`mathmodel-diagram`）

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

---

## 五、代码风格

- Python：4 空格缩进，标准库优先；脚本用 `argparse`，参数风格对齐既有脚本
  （`-o/--out`、`--check`、`--list`、`--lang`）；
- **退出码语义**：`0` 成功 / `1` 校验或渲染失败 / `2` 用法或环境错误；
- 注释与文档字符串用中文（与仓库一致），面向用户的消息提供 `--lang {zh,en}` 时中英并行；
- 不引入新的格式化/检查工具链（仓库不依赖 ruff/black/pytest）；
- 不提交生成物（工作区目录、`.aux`、PDF/PNG 产物等，见 `.gitignore`）。

---

## 六、提交与 PR

提交信息沿用仓库既有风格：`<type>(<scope>): <中文摘要>`，`type` 取
`feat` / `fix` / `docs` / `refactor` / `chore`，正文说明**为什么**改（而非复述改了什么）。

PR 请使用仓库的 PR 模板，逐项确认。CI 必须全绿，包含：

| 检查 | 内容 |
|---|---|
| `syntax` | 全部 Python 脚本可编译 |
| `manifest-consistency` | 注册表 ↔ 文件系统 ↔ 索引文档 ↔ 版本号 ↔ README 徽章 互相一致 |
| `manifest-consistency` | JSON Schema 本身合法，且全部内置示例通过严格校验 |
| `figures` / `diagrams` | 每个模板都能渲染出非空产物 |
| `strip-invisible` | 零宽字符清理器往返行为正常 |
| `Paper LaTeX build` | 论文骨架可编译 |

---

## 七、评审口径

机器能判定的（语法、一致性、Schema、渲染成功）交给 CI，**人只评审机器判不了的**：

- 槽位**语义**是否正确（并列/汇流/对比放错，比字数超框严重得多）；
- 文案是否忠于来源材料（**禁止编造数据与文献**）；
- 字数预算是否**实测**得出（不接受手估）；
- 是否值得做成模板。

拒收情形：编造数据或文献；语义标注错误；只改观感却破坏既有调用契约（CLI 参数、注册表字段、产物路径）。

---

## 八、署名与许可

本项目以 [Apache-2.0](LICENSE) 分发，贡献即表示同意以同一许可发布。

模板作者会在对应注册表的 `author` 字段**永久署名**，并在模板目录中与官方模板并列展示；
修复与文档贡献会记入 [CHANGELOG.md](CHANGELOG.md) 并在 Release notes 中致谢。

---

## 九、行为准则

就事论事，对事不对人；技术分歧以**可复现的证据**为准（命令、输入、输出），而不是以资历或篇幅为准。
不接受任何形式的抄袭、数据伪造与文献编造。
