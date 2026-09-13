# mathmodel-methods

数学建模方法库与选型模块：按问题族给出候选方法、适用边界、实现入口与验证方式。入口文件是 [SKILL.md](SKILL.md)；
本 README 只说明目录组织，与 `mathmodel-core`、`mathmodel-figure`、`mathmodel-diagram` 采用同一套分类规范。

## 目录结构

```
mathmodel-methods/
├── SKILL.md                       # 技能入口：快速路径、选型三原则、问题族速查、边界与分工
├── README.md                      # 本文件：结构说明
└── docs/                          # 方法论（不绑定具体题目与代码）
    ├── method-library.md          #   方法库（唯一出处）：问题族索引 + 九类方法清单 + 收录标准
    ├── selection-guide.md         #   选型指南：选型流程、候选对比表、问题特征对照、验证方式、递进关系、常见误用
    └── implementation-guide.md    #   实现指南：推荐库速查、最小可运行骨架、实现纪律、技能分工
```

## 分类依据

- **一级按内容类型分**（`docs/`）：与 `mathmodel-core` 同属「规范与知识」型技能，不含可执行脚本，
  故只有 `docs/`；新增方法论一律进 `docs/`，不引入新的顶层目录。
- **二级按用途分**：`method-library.md` 是**方法清单的唯一出处**，`selection-guide.md` 管「怎么选」，
  `implementation-guide.md` 管「怎么实现」；三者互相链接、职责不重叠。
- **规范条文不在此仓库复制**：论文写作与评分口径分别以 `mathmodel-paper` / `mathmodel-score` 为准，
  出图规范以 `mathmodel-figure` 为准；本技能只承接「方法与选型」这一类，避免两处规范漂移。
- **层级最深 2 层**。

## 与主技能的关系

主技能 `mathmodel-core` 的阶段三（算法选择）与阶段四（代码实现）按本技能执行；核心方法清单不在主技能复述，
主技能只保留强制项摘要与链接。这样方法库可以独立迭代与协作维护，主技能的阶段编排保持稳定。

## 扩展约定

新增方法或调整选型口径的交付清单：

```
docs/method-library.md             # 按收录标准加一条（问题族索引 + 所属分类）
docs/selection-guide.md            # 同步问题特征对照、验证方式与常见误用
docs/implementation-guide.md       # 同步推荐库与最小骨架（如需）
SKILL.md                           # 问题族速查表加一行（如涉及新问题族）
```

约定：

- 方法必须写明适用场景、数据规模前提与已知失效情形，并给出可复核出处（标准教材或原始文献）；
- 用户可见的结论不给绝对化判断：本技能提供候选与依据，最终选型由使用者确认；
- 分模块的贡献标准、提交规范与审核流程见仓库根目录 [CONTRIBUTING.md](../../CONTRIBUTING.md)
  （方法库与选型文档属 M1 文档与示例）；本节只列本技能的落盘清单。
