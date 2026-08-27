# mathmodel-paper

数学建模论文排版模板与输出工具链（LaTeX 骨架 + pandoc 转 Word + python-docx 版式微调 + 摘要模板）。入口文件是 [SKILL.md](SKILL.md)，本 README 只说明目录组织，与 `mathmodel-figure`、`mathmodel-diagram` 采用同一套分类规范。

## 目录结构

```
mathmodel-paper/
├── SKILL.md                        # 技能入口：定位、快速流程、页面设置速查、匿名红线
├── README.md                       # 本文件：结构说明
├── code/                           # 可执行脚本
│   └── word_postprocess.py         #   pandoc 转换后的 Word 版式微调（仅改样式，禁止重建内容/手工插入公式）
└── templates/                      # 可复制骨架
    ├── paper.tex                   #   LaTeX 论文骨架（复制填写，含全部规范注释）
    └── abstract-template.md        #   摘要写作模板 + 关键要求 + 摘要页分页规则
```

## 分类依据

- **一级按内容类型分**（`code/` `templates/`）：与 `mathmodel-figure`（`code/templates`、`code/tools`）、`mathmodel-diagram`（`code/templates`、`docs/templates`、`examples/`）共用同一份目录词表，跨技能检索时 `code/` 恒为「可执行脚本」、`templates/` 恒为「可复制骨架」，语义不变。
- **`code/` = 可执行脚本**：命令行直接跑、有 `argparse` 入口、原地作用于产物（此处即 pandoc 生成的 `.docx`）。
- **`templates/` = 可复制骨架**：不参与执行，复制到工作区后填写；`.tex` 是文档骨架，`.md` 是写作模板，二者同为「拿来即用」的空白件。
- **规范条文不在此仓库复制**：论文结构、语言表述、自检清单、百分制评分留在主技能 `math-modeling-helper/SKILL.md`，本技能只放落地件与速查摘要，避免两处规范漂移。
- **层级最深 2 层**，新增模板只需在 `templates/` 加同名条目。

## 扩展约定

新增模板/脚本的交付清单：

```
templates/<template_name>           # 骨架或写作模板（含出处注释与用法说明）
SKILL.md                            # 「快速流程」或「目录结构」登记一行；必要时补速查表/红线清单
code/<script>.py                    # 若该模板需要配套可执行处理，则新增脚本并加 docstring 说明角色边界
```

约定：

- 模板文件头部注明**提取源**（主技能 SKILL.md 的哪一小节），便于主技能瘦身后的双向定位。
- 脚本一律提供 `argparse` 入口与默认路径，不写死绝对路径；只调整既有内容样式，禁止生成或重建正文。
- 不引入新的顶层目录；需要说明性长文档时再评估是否并入 `docs/`（与 figure/diagram 同词表）。
