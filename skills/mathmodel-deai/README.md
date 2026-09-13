# mathmodel-deai

降 AI 模块：论文去 AI 化（表述级）与交付前不可见字符清理（字符级）。入口文件是 [SKILL.md](SKILL.md)，规范条文以 [docs/deai-rules.md](docs/deai-rules.md) 为唯一权威；本 README 只说明目录组织，与 `mathmodel-figure`、`mathmodel-diagram`、`mathmodel-paper` 采用同一套分类规范。

## 目录结构

```
mathmodel-deai/
├── SKILL.md                       # 技能入口：定位、快速流程、强制项摘要、与其他技能的关系
├── README.md                      # 本文件：结构说明
├── code/                          # 可执行脚本与数据
│   ├── check_phrasing.py          #   词表级检查器：扫模板腔/套话/空泛/伪洞察，命中退出 1
│   ├── phrasing-blacklist.json    #   去 AI 词表与句式规则（单一事实源，加词只改它）
│   ├── check_style.py             #   结构级检查器：句长/被动句、句式重复、过渡密度、段落节奏、小数位、风险等级
│   └── strip_invisible.py         #   字符级清理器：零宽/不可见 Unicode，覆盖 tex/docx/pdf
├── docs/                          # 规范
│   ├── deai-rules.md              #   降 AI 规范（唯一权威）：痕迹清单、改写规则、负面清单、个性化、摘要去模板化、结构级十项细则与三关门禁
│   └── no-ai-slop-reference.md    #   英文参考：AI slop 模式清单（整理自 petergyang/no-ai-slop，MIT，含来源 SHA 与版权声明）
└── examples/                      # 可复现示例
    ├── clean-sample.tex           #   正例：合规写法（两检查器都应零命中）
    ├── slop-sample.tex            #   反例：中文词汇/句式痕迹密集（check_phrasing 应密集命中）
    ├── style-slop-sample.tex      #   反例：结构痕迹密集（check_style 应命中六项指标）
    ├── clean-sample-en.md         #   正例（英文）：合规写法
    └── slop-sample-en.md          #   反例（英文）：en-slop-* 规则密集
```

## 分类依据

- **一级按内容类型分**（`code/` `docs/` `examples/`）：与 `mathmodel-figure`、`mathmodel-diagram`、`mathmodel-paper` 共用同一份目录词表，跨技能检索时语义不变——`code/` 恒为「可执行脚本与数据」、`docs/` 恒为「规范」、`examples/` 恒为「可复现示例」。
- **词表是数据不是代码**：`phrasing-blacklist.json` 是可被检查器读取、可被第三方程序消费的规则数据；加词只改这一处，`docs/deai-rules.md` 与检查器同步生效。
- **字符集移植自上游**：`strip_invisible.py` 的字符集与保护逻辑来自 [watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) 的 Layer A；句式规则与结构指标分类参考 [no-ai-slop](https://github.com/petergyang/no-ai-slop)，其英文 slop 模式清单整理为 `docs/no-ai-slop-reference.md`（MIT，保留上游版权声明与来源 SHA），中文规则与词表出处写在 `docs/deai-rules.md` 第九节。
- **规范条文不在此仓库复制**：正文写作与排版条文在 `mathmodel-paper/docs/`，评分条文在 `mathmodel-score/docs/`，本技能只承接「去 AI 化 + 字符清理」这一类，避免两处规范漂移。
- **层级最深 2 层**。

## 扩展约定

新增规则或清理规则集的交付清单：

```
code/phrasing-blacklist.json       # 在 rules 中加一条（id/label/severity/why/fix/patterns/max_per_document）
docs/deai-rules.md                 # 对应补一行说明（反例写成行内代码，检查器会跳过，故文档可自检）
examples/                          # 必要时补正/反例 fixture
```

约定：

- 词表规则一律带 `why`（为什么算痕迹）与 `fix`（怎么改），检查器输出直接引用，保证「报出即有改法」。
- 结构级阈值（句长/段落/小数位等）写在 `code/check_style.py` 头部常量；调整后须同步 `docs/deai-rules.md` 6.1 与 `examples/` 的期望结果。
- 正则用 Python `re` 语法；写错正则应报错而非静默跳过（加载时预编译）。
- 规范文档里出现的反例一律用反引号包成行内代码，使其自身通过 `check_phrasing.py` 自检。
- 脚本一律提供 `argparse` 入口，退出码统一为 `0` 成功 / `1` 校验失败 / `2` 用法或环境错误。
- 分模块的贡献标准、提交规范与审核流程见仓库根目录 [CONTRIBUTING.md](../../CONTRIBUTING.md)（词表与规范文档属 M1/M2，示例回归属 M3）。
