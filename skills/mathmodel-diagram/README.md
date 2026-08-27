# mathmodel-diagram

JSON 驱动的学术示意图渲染技能（matplotlib）。入口文件是 [SKILL.md](SKILL.md)，本 README 只说明目录组织。

## 目录结构

```
mathmodel-diagram/
├── SKILL.md                # 技能入口：三条路径（套模板 / 手写 / 复刻）+ 渲染命令
├── README.md               # 本文件：结构说明
├── code/                   # 全部 Python 源码
│   ├── common.py           #   基元层：画布/字体探测/字宽校验/绘图基元/Recorder/保存
│   └── templates/          #   5 个 JSON 驱动模板，与 docs/templates/、examples/ 一一对应
│       ├── roadmap_5band.py     # 五带技术路线图（954×1296 竖版）
│       ├── framework_3col.py    # 三栏研究框架图（内容全景）
│       ├── stageflow_3col.py    # 三栏阶段流程图（执行流程）
│       ├── taskflow_land.py     # 横版任务流水线图（1360 宽）
│       └── problem_flow.py      # 问题分析流程图（论文第二章必插）
├── docs/                   # 全部 Markdown 文档
│   ├── templates/          #   模板说明：语义约定 + 槽位字数预算
│   │   ├── roadmap-5band.md
│   │   ├── framework-3col.md
│   │   ├── stageflow-3col.md
│   │   ├── taskflow-land.md
│   │   ├── problem-flow.md
│   │   └── adding-templates.md  # 新增模板的契约与交付清单
│   └── guides/             #   通用方法论（不绑定具体模板）
│       ├── authoring.md          # 从零手写：骨架、基元速查、字宽预算、连接器
│       ├── replication.md        # 高保真复刻：标定、四件产物、迭代闭环
│       └── self-check.md         # 九区盘点、红队复审、评分卡、交付清单
└── examples/               # 模板示例（可复现源），每个模板一个目录
    ├── roadmap-5band/      #   example.json（填满的真实示例）+ preview.png（1:1 效果）
    ├── framework-3col/
    ├── stageflow-3col/
    ├── taskflow-land/
    └── problem-flow/
```

## 分类依据

- **一级按内容类型分**（`code/` `docs/` `examples/`）：与 `mathmodel-figure`、`math-modeling-helper` 同一套目录词表，跨技能检索时语义相同。
- **二级按功能模块分**：`code/templates ↔ docs/templates ↔ examples` 三者以模板 id 同名对齐，改一个模板时三个位置一起改；`common.py` 是全部模板共用的基元层；`docs/guides` 收纳跨模板的通用方法论。
- **层级最深 2 层**，命名统一小写连字符（目录/模板 id）与下划线（Python 模块）。

## 技术栈约定

- 渲染一律经 `code/common.py`：坐标系 1 px = 0.01 inch、y 轴向下，drawio 时代标定的几何常量原值复用；
- 每个模板写文件前逐槽中文字宽校验（全角=字号、半角=字号/2、行高=字号+3），超框非零退出报预算；
- 产物固定为 PNG 300dpi + 同名矢量 PDF（`pdf.fonttype=42`，中文在 PDF 里保持可编辑文本）。

## 扩展约定

新增模板按 [docs/templates/adding-templates.md](docs/templates/adding-templates.md) 的交付清单操作：

```
code/templates/<template_id>.py        # 渲染器（基于 common.py 基元）
docs/templates/<template_id>.md        # 语义 + 字数预算
examples/<template_id>/example.json    # 真实示例
examples/<template_id>/preview.png     # 用本渲染器导出的 1:1 预览
SKILL.md                               # 模板索引表加一行
```
