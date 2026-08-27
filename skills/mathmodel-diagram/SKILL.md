---
name: mathmodel-diagram
description: 用 matplotlib 渲染学术示意图（JSON 驱动，产出 PNG 300dpi + 矢量 PDF），五条内置模板：五带技术路线图、三栏研究框架图、三栏阶段流程图、横版任务流水线图、问题分析流程图（论文第二章必插）。当用户要求技术路线图、全文概览、研究框架图、问题分析图、论文流程图、算法流程图、模型/系统架构图、方法示意图、把论文或课题做成一张图、答辩用图，或要求照着某张参考图高保真重画、修图（文字溢出/箭头错乱/配色不一致/排版对不齐）时使用。画折线图热图等数据图表请改用 mathmodel-figure。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 学术示意图渲染器（matplotlib）

主产物是 **PNG（300dpi）+ 矢量 PDF**，可编辑的源是渲染脚本 + content JSON。
模板、手写、复刻、校验、保存全在 `code/common.py` 与模板脚本内，仅依赖 matplotlib 与 numpy（与本套件其他技能一致）；C 路径的标定脚本另需 scipy / Pillow（见 replication.md）。

## 先判断走哪条路

| 情况 | 路径 | 入口 |
|---|---|---|
| 全文脉络、研究框架、执行流程、课题任务分解、论文第二章问题分析图 | **A 套模板** | 下方模板索引 |
| 其他示意图：算法流程、模型架构、实验设计、机制示意… | **B 从零手写** | `docs/guides/authoring.md` |
| 给了参考图，要照着重画成高保真渲染图 | **C 高保真复刻** | `docs/guides/replication.md` |

三条路的绘图基元一致（同一套 `common.py`），产物格式互通，可在任一路径上继续修改；区别只在**流程纪律的严格程度**。

## A. 套模板

| 模板 id | 版式 | 适合表达 | 说明 |
|---|---|---|---|
| `roadmap-5band` | 954×1296 竖版，五条点线带 + 左旗标 + 右竖排标签 | 提出问题 → 数据与指标 → 方法与机制 → 结果对比 → 评价推广 | `docs/templates/roadmap-5band.md` |
| `framework-3col` | 1026 宽三栏，左阶段链 / 中内容块 / 右方法清单，高度自适应 | 研究**内容**全景：每个阶段对应哪些研究内容、用什么方法 | `docs/templates/framework-3col.md` |
| `stageflow-3col` | 1000 宽三栏，中栏每块实色标题条 + 独立色系，高度自适应 | 研究/系统的**执行流程**：阶段推进、决策分支、成果分发 | `docs/templates/stageflow-3col.md` |
| `taskflow-land` | **横版** 1360 宽，若干任务块，块内流水线 + 每步挂做法细节 | 课题拆成「任务一…任务四」，每步要写清方法与结论；适合 16:9 | `docs/templates/taskflow-land.md` |
| `problem-flow` | 任意画布，总分布局（顶层居中→并行分支→底层收拢）+ 反馈虚线 | 论文**第二章问题分析图**、简单系统/方法架构图 | `docs/templates/problem-flow.md` |

1. 读模板说明的两节：**语义约定**（哪些槽位并列、哪些汇流、哪两组必须可对比）与**字数预算**。语义放错比字数超框严重得多。
2. 从用户材料抽内容，**不要编**；有源文件（`.tex`/`.md`/代码）时逐个核对数值，术语用原文。
3. 复制 `examples/<template_id>/example.json` 改写，`"\n"` 手动断行。
4. 渲染（写文件前逐槽校验字数，超框报出具体预算并以非零码退出）：

```bash
python3 code/templates/roadmap_5band.py  content.json -o out.png   # 模板 roadmap-5band
python3 code/templates/framework_3col.py content.json -o out.png   # 模板 framework-3col
python3 code/templates/stageflow_3col.py content.json -o out.png   # 模板 stageflow-3col
python3 code/templates/taskflow_land.py  content.json -o out.png   # 模板 taskflow-land（横版）
python3 code/templates/problem_flow.py   content.json -o out.png   # 模板 problem-flow（问题分析图）
```

每个模板同时产出同名 `.pdf`（矢量）。只要校验不要出图：把 `-o ...` 换成 `--check`。

新增模板见 `docs/templates/adding-templates.md`。

## B. 从零手写

读 `docs/guides/authoring.md`：骨架、基元速查、中文字宽预算、连接器写法、四个必踩的坑。

三条最容易翻车的：

- **先排栅格再写图元**：定死画布、列基线、步距；同族同宽同步距，数量可变的组用 `slots()` 等分。
- **中文手动断行**：全角≈字号、半角≈字号/2、行高≈字号+3；16px 字号下 240px 宽的盒子每行最多 14 个汉字。竖排逐字堆叠（`stack()`），**不要用 rotation 旋转整段中文**。
- **连接器端点离盒边 1px**；一分多/多合一画成"竖线+横母线+分支"，不要画成 N 条独立斜线。

画之前想清楚每根箭头的语义（谁到谁、单向还是双向、扇入还是扇出）；说不出含义的箭头不要画。

## C. 高保真复刻参考图

比 B 多一套证据链，照 `docs/guides/replication.md` 执行，要点：

1. **先标定再动笔**：用连通域提取盒子坐标与填充色、按行列扫描找框线、逐色普查取配色、量字宽反推字号。**不要目测**，也不要假设"标题一定比正文大"。
2. **四件中间产物**：`visual-spec.md`（看到了什么）、`layout-grid.md`（坐标计划）、`asset-ledger.md`（哪些是近似的，防止悄悄丢元素）、`defect-log.md`（首次截图后只增不改）。
3. **≥3 轮**"截图 → 九区盘点 → 修完所有 P0/P1 → 重渲 → 逐条核销"；截图必须是画布本身。
4. **红队复审 + 自评分卡**（见 `docs/guides/self-check.md`）：总分 <40 或任一维 ≤4 不交付。
5. 像素差分定位残留差异，逐条写进 `defect-log.md`，不写"已完美还原"。

## 通用：校验、预览、交付

- **机器门禁**：每个模板写文件前逐槽跑中文字宽校验，超框报出槽位与预算并以非零码退出——正常的渲染应当**一次通过**，报警就值得认真看。
- **字体**：`common.py` 自动探测 SimHei → Microsoft YaHei → Noto Sans CJK → 文泉驿，全缺时告警（图中中文会是方框，必须装字体再出图）。

**不看渲染图不算画完**：代码里看不出文字溢出、箭头压字、盒子挤扁。打开 PNG 至少逐项过一遍：① 文字溢出/压线；② 箭头方向与语义；③ 同族元素对齐同宽；④ 数值有没有抄错。完整的九区盘点与交付清单见 `docs/guides/self-check.md`。

交付 PNG + PDF，走模板路径时保留 content JSON 作为可复现源。尺寸提醒：954px 宽、16px 字号的图压到 A4 正文 `0.97\textwidth` 约 6.5pt，建议整页横排或答辩使用，正文小图另做精简版。

## 参考索引

| 文件 | 何时读 |
|---|---|
| `docs/guides/authoring.md` | 手写示意图：骨架、基元速查、字宽预算、连接器 |
| `docs/templates/roadmap-5band.md` | 用五带路线图模板 |
| `docs/templates/framework-3col.md` | 用三栏研究框架模板（内容全景）|
| `docs/templates/stageflow-3col.md` | 用三栏阶段流程模板（执行流程）|
| `docs/templates/taskflow-land.md` | 用横版任务流水线模板 |
| `docs/templates/problem-flow.md` | 用问题分析流程图模板（第二章配图）|
| `docs/templates/adding-templates.md` | 新增一个模板 |
| `docs/guides/replication.md` | 复刻参考图：标定方法、四件产物、迭代闭环 |
| `docs/guides/self-check.md` | 九区盘点、红队复审、自评分卡、交付清单 |

## 不适用

- 折线图、热图、统计图等**数据图表** → 用 `mathmodel-figure` 技能；
- 需要 LaTeX 排版的公式推导链 → 用 TikZ 或写进正文。
