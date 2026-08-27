---
name: scibox-diagram
description: 制作与修改可编辑的 draw.io / diagrams.net 示意图（.drawio XML），产出 .drawio + PNG/PDF。三条路径：套用内置模板（五带技术路线图、三栏研究框架图、三栏阶段流程图、横版任务流水线图）、从零手写 XML、高保真复刻参考图。当用户要求技术路线图、全文概览、研究框架图、论文流程图、算法流程图、模型/系统架构图、方法示意图、把论文或课题做成一张图、答辩用图，或要求画 drawio 图、照着某张图重画成可编辑矢量图、修图（文字溢出/箭头错乱/配色不一致/排版对不齐）时使用。画折线图热图等数据图表请改用 scibox-figure。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 论文与研究示意图（draw.io）

主产物是**可编辑的 .drawio**，PNG/PDF 是附带导出。模板、手写、复刻、校验、预览、导出全在本目录内。

## 先判断走哪条路

| 情况 | 路径 | 入口 |
|---|---|---|
| 全文脉络、研究框架、执行流程，或课题的任务分解 | **A 套模板** | 下方模板索引 |
| 其他示意图：算法流程、模型架构、实验设计、机制示意… | **B 从零手写 XML** | `references/authoring.md` |
| 给了参考图，要照着重画成可编辑矢量图 | **C 高保真复刻** | `references/replication.md` |

三条路的 XML 写法一致，产物可互相接着改；区别只在**流程纪律的严格程度**。

## A. 套模板

| 模板 id | 版式 | 适合表达 | 说明 |
|---|---|---|---|
| `roadmap-5band` | 954×1296 竖版，五条点线带 + 左旗标 + 右竖排标签 | 提出问题 → 数据与指标 → 方法与机制 → 结果对比 → 评价推广 | `references/roadmap-5band.md` |
| `framework-3col` | 1026 宽三栏，左阶段链 / 中内容块 / 右方法清单，高度自适应 | 研究**内容**全景：每个阶段对应哪些研究内容、用什么方法 | `references/framework-3col.md` |
| `stageflow-3col` | 1000 宽三栏，中栏每块实色标题条 + 独立色系，高度自适应 | 研究/系统的**执行流程**：阶段推进、决策分支、成果分发 | `references/stageflow-3col.md` |
| `taskflow-land` | **横版** 1360 宽，若干任务块，块内流水线 + 每步挂做法细节 | 课题拆成「任务一…任务四」，每步要写清方法与结论；适合 16:9 | `references/taskflow-land.md` |

1. 读模板说明的两节：**语义约定**（哪些槽位并列、哪些汇流、哪两组必须可对比）与**字数预算**。语义放错比字数超框严重。
2. 从用户材料抽内容，**不要编**；有源文件（`.tex`/`.md`/代码）时逐个核对数值，术语用原文。
3. 复制 `assets/<template_id>/example.json` 改写，`"\n"` 手动断行。
4. 渲染（写文件前逐槽校验字数，超框报出具体预算）：

```bash
python3 scripts/roadmap_5band.py content.json -o out.drawio     # 模板 roadmap-5band
python3 scripts/framework_3col.py content.json -o out.drawio    # 模板 framework-3col
python3 scripts/stageflow_3col.py content.json -o out.drawio    # 模板 stageflow-3col
python3 scripts/taskflow_land.py  content.json -o out.drawio    # 模板 taskflow-land（横版）
```

新增模板见 `references/adding-templates.md`。

## B. 从零手写 XML

读 `references/authoring.md`：骨架、样式速查、中文字宽预算、连接器写法、四个必踩的坑。图标与特殊图元见 `references/icons.md`。

三条最容易翻车的：

- **先排栅格再写图元**：定死画布、列基线、步距；同族同宽同步距，数量可变的组用等分公式。
- **中文手动断行**：全角≈字号、半角≈字号/2、行高≈字号+3；16px 字号下 160px 宽的盒子每行最多 9 个汉字。竖排逐字 `&lt;br&gt;` 堆叠，**不要用 `horizontal=0`**（中文会躺倒）。
- **连接器端点离盒边 1px**；一分多/多合一画成"竖线+横母线+分支"，不要画成 N 条独立斜线。

画之前想清楚每根箭头的语义（谁到谁、单向还是双向、扇入还是扇出）；说不出含义的箭头不要画。

## C. 高保真复刻参考图

比 B 多一套证据链，照 `references/replication.md` 执行，要点：

1. **先标定再动笔**：连通域抠盒子坐标与填充色、行列扫描找框线、颜色普查取配色、量字宽反推字号。**不要目测**，也不要假设"标题一定比正文大"。
2. **四件中间产物**：`visual-spec.md`（看到了什么）、`layout-grid.md`（坐标计划）、`asset-ledger.md`（哪些是近似的，防止悄悄丢元素）、`defect-log.md`（首次截图后只增不改）。
3. **≥3 轮**"截图 → 九区盘点 → 修完所有 P0/P1 → 重渲 → 逐条核销"；截图必须是画布本身。
4. **红队复审 + 自评分卡**（见 `references/self-check.md`）：总分 <40 或任一维 ≤4 不交付。
5. 像素差分定位残留差异，逐条写进 `defect-log.md`，不写"已完美还原"。

## 通用：校验、预览、导出

```bash
python3 scripts/check_layout.py fig.drawio      # 溢出/越界/重复 id/重叠/穿盒/位图（--strict 作门禁）
python3 scripts/export_figure.py fig.drawio     # 1:1 PNG + 矢量 PDF（需 drawio 命令行）
python3 scripts/preview_html.py fig.drawio      # 浏览器预览，无需 drawio 命令行
```

`check_layout` 用中文字宽模型、噪声低，正常的图应当 **FAIL 0 / WARN 0**；报警就值得认真看。它刻意不查紧密堆叠的行列间距和同族尺寸对齐（前者是刻意排版，后者机器判族必然误报）——这两项交给眼睛。规则详解与四个规避手法见 `references/preflight-rules.md`。

**不看渲染图不算画完**：XML 里看不出文字溢出、箭头压字、盒子挤扁。打开 PNG 至少过两轮：① 文字溢出/压线；② 箭头方向与语义；③ 同族元素对齐同宽；④ 数值有没有抄错。完整的九区盘点与交付清单见 `references/self-check.md`。

交付 `.drawio` + PNG/PDF；走模板路径时保留 content JSON 作为可复现源。尺寸提醒：954px 宽、16px 字号的图压到 A4 正文 `0.97\textwidth` 约 6.5pt，建议整页横排或答辩使用，正文小图另做精简版。

## 参考索引

| 文件 | 何时读 |
|---|---|
| `authoring.md` | 手写示意图：骨架、样式串、字宽预算、连接器 |
| `icons.md` | 需要图标、旗标、块箭头、弯箭头等特殊图元 |
| `roadmap-5band.md` | 用五带路线图模板 |
| `framework-3col.md` | 用三栏研究框架模板（内容全景）|
| `stageflow-3col.md` | 用三栏阶段流程模板（执行流程）|
| `taskflow-land.md` | 用横版任务流水线模板 |
| `adding-templates.md` | 新增一个模板 |
| `replication.md` | 复刻参考图：标定方法、四件产物、迭代闭环 |
| `self-check.md` | 九区盘点、红队复审、自评分卡、交付清单 |
| `preflight-rules.md` | 静态检查在查什么、误报如何绕开 |

## 不适用

- 折线图、热图、统计图等**数据图表** → 用 `scibox-figure` 技能；
- 需要 LaTeX 排版的公式推导链 → 用 TikZ 或写进正文。
