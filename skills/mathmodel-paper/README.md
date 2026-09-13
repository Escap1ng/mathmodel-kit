# mathmodel-paper

数学建模论文**写作与排版**技能：论文写作规范、LaTeX 骨架与页面设置、pandoc 转 Word、python-docx 版式微调、参考文献规范。
入口文件是 [SKILL.md](SKILL.md)，本 README 只说明目录组织，与 `mathmodel-figure`、`mathmodel-diagram`、`mathmodel-deai` 采用同一套分类规范。

## 目录结构

```
mathmodel-paper/
├── SKILL.md                        # 技能入口：定位、文档地图、快速流程、交付红线
├── README.md                       # 本文件：结构说明
├── code/                           # 可执行脚本
│   └── word_postprocess.py         #   pandoc 转换后的 Word 版式微调（仅改样式，禁止重建内容/手工插入公式）
├── docs/                           # 规范（人读，唯一权威）
│   ├── writing-rules.md            #   论文写作规范：结构/摘要五段式/模型建立与求解/公式/评价/附录/语言表述
│   ├── typesetting-rules.md        #   排版规范：页面设置/强制规范/匿名红线/LaTeX 骨架说明/Word 后处理
│   └── references.md               #   参考文献规范：GB/T 7714 著录、数量建议、引用查证流程
└── templates/                      # 可复制骨架
    ├── paper.tex                   #   LaTeX 论文骨架（复制填写，含全部规范注释）
    └── abstract-template.md        #   摘要写作模板 + 关键要求 + 摘要页分页规则
```

## 分类依据

- **一级按内容类型分**（`code/` `docs/` `templates/`）：与 `mathmodel-figure`、`mathmodel-diagram`、`mathmodel-deai`、
  `mathmodel-score` 共用同一份目录词表，跨技能检索时语义不变——`code/` 恒为「可执行脚本」、
  `docs/` 恒为「规范（唯一权威）」、`templates/` 恒为「可复制骨架」。
- **论文域条文收敛在本技能**：写作、排版与参考文献规范以本技能 `docs/` 为唯一权威；主技能 `mathmodel-core`
  只保留强制项摘要与链接，`mathmodel-score` 的章节结构契约与 `mathmodel-deai` 的表述口径各自独立、互不复述。
- **规范与落地件分开放**：`docs/` 是条文，`templates/` 是空白件，`code/` 是对产物生效的脚本；
  改条文不动脚本，改脚本不改条文。
- **`code/` = 可执行脚本**：命令行直接跑、有 `argparse` 入口、原地作用于产物（此处即 pandoc 生成的 `.docx`）。
- **`templates/` = 可复制骨架**：不参与执行，复制到工作区后填写；`.tex` 是文档骨架，`.md` 是写作模板。
- **层级最深 2 层**，新增规范进 `docs/`，新增骨架进 `templates/`。

## 扩展约定

新增规范条文、骨架或脚本的交付清单：

```
docs/<topic>.md                     # 规范条文（首行声明「唯一权威出处」，并同步 SKILL.md 文档地图）
templates/<template_name>           # 骨架或写作模板（含出处注释与用法说明）
code/<script>.py                    # 若需配套可执行处理，则新增脚本并加 docstring 说明角色边界
SKILL.md                            # 「文档地图」或「目录结构」登记一行；必要时补速查表/红线清单
```

约定：

- 模板文件头部注明**出处**（论文域条文以本技能 `docs/` 为准），便于双向定位。
- 脚本一律提供 `argparse` 入口与默认路径，不写死绝对路径；只调整既有内容样式，禁止生成或重建正文。
- 不引入新的顶层目录；`docs/` 的文件名用小写连字符。
- 分模块的贡献标准、提交规范与审核流程见仓库根目录 [CONTRIBUTING.md](../../CONTRIBUTING.md)（论文规范属 M1 文档与示例）；本节只列本技能的落盘清单。
