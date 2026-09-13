---
name: mathmodel-methods
description: 数学建模方法库与选型技能：按问题族（评价/排序、优化、预测、分类聚类、微分方程、仿真、信号处理、前沿创新）给出候选算法、适用边界、实现入口与验证方式，覆盖基础数值、经典优化、图论网络、群体智能、机器学习、统计与数据挖掘、综合评价、物理工程建模与前沿方法，并附候选对比表模板、问题递进关系与常用库速查。当用户问"这题用什么算法""推荐建模方法""算法选型对比""某类问题怎么建模求解"时使用；论文写作、排版、出图、去 AI 与评分分别改用 mathmodel-paper / mathmodel-figure / mathmodel-diagram / mathmodel-deai / mathmodel-score。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# 数学建模方法库与选型（mathmodel-methods）

把「某类问题该用什么方法」做成可检索、可对比、可复核的知识层：方法清单、选择依据、实现入口、
验证方式各自成文，方法名与适用边界以本技能为唯一出处。**方法选型的最终判断仍由使用者做出**，
本技能给候选与依据，不给标准答案。

## 快速路径

1. **给问题定性**：判断子问题属于哪个问题族（优化 / 预测 / 评价 / 分类 / 微分方程 / 仿真 / 信号），
   依据是数据结构、约束条件与要回答的结论，而不是题目出现的章节顺序。
2. **取候选**：按 [docs/selection-guide.md](docs/selection-guide.md) 的「问题族 → 首选/备选」表取 2–3 个候选
   （至少 1 个具备创新性），方法细节查 [docs/method-library.md](docs/method-library.md)。
3. **出对比表并交由用户选择**：用 [docs/selection-guide.md](docs/selection-guide.md) 的候选对比表模板，
   标注推荐项与一句推荐理由；用户确认后再实现。
4. **实现与验证**：[docs/implementation-guide.md](docs/implementation-guide.md) 给出推荐库、最小可运行骨架
   与按问题类型匹配的验证手段；出图交给 `mathmodel-figure` / `mathmodel-diagram`，成稿交给 `mathmodel-paper`。

## 选型三原则（强制）

1. **拟合性优先于高级性**：先选与问题结构、数据规模、约束条件最匹配的方法（可求解、结果可靠、可解释），
   再在匹配的基础上考虑创新性；禁止为炫技引入与问题不适配的高深算法。
2. **方法梯度**：能用初等方法解决的不用高等方法，能用简单方法解决的不用复杂方法，
   能用被更多人看懂的方法不用只有少数人看懂的方法。
3. **创新需回答一个问题**：创新点要说明「解决了旧方法解决不了的什么问题」；适配与创新冲突时适配优先。

## 问题族速查

| 问题族 | 首选 | 备选与延伸 |
|---|---|---|
| 评价 / 排序 | 熵权-TOPSIS | AHP、CRITIC、灰色关联分析、模糊综合评价、DEA |
| 优化（连续 / 非线性） | 非线性规划（SLSQP / trust-constr） | 凸问题 cvxpy；多目标 NSGA-II/III |
| 优化（离散 / 组合） | 整数规划（pulp / CBC） | GA、SA、PSO、ACO、分支定界、动态规划 |
| 预测（时序） | ARIMA / Prophet | LSTM/GRU、Holt-Winters、VAR；小样本优先灰色预测 |
| 预测（小样本 / 贫信息） | 灰色预测 GM(1,1) | 马尔可夫链、组合预测 |
| 回归 / 拟合 | 统计推断 statsmodels | 纯预测 sklearn；响应面、GPR、岭回归 / Lasso |
| 分类 / 判别 | 逻辑回归 / XGBoost | SVM、随机森林、LightGBM、Fisher 判别、朴素贝叶斯 |
| 聚类 / 降维 | K-means / DBSCAN | 层次聚类、GMM、PCA、t-SNE、UMAP |
| 微分方程 / 机理（A 题） | 微分方程组 + RK4 | 有限差分、SIR/SEIR、平衡点与相图 |
| 仿真 | 蒙特卡洛 | DES、元胞自动机、多智能体仿真、排队论 |
| 信号处理 | FFT | 小波、EMD、卡尔曼滤波、HHT |
| 前沿创新 | PINN / 符号回归 / SHAP | NSGA-II/III、因果推断、GNN、算子学习 |

> 速查表只用于定位方向，方法与边界以 [docs/method-library.md](docs/method-library.md) 为准。

## 文档地图

| 你要做什么 | 看哪份 |
|---|---|
| 查方法清单、适用场景与代表算法 | [docs/method-library.md](docs/method-library.md) |
| 选型流程、候选对比表、问题递进、常见误用 | [docs/selection-guide.md](docs/selection-guide.md) |
| 推荐库、最小可运行骨架、验证手段 | [docs/implementation-guide.md](docs/implementation-guide.md) |
| 走完整个竞赛流程（阶段编排） | [`mathmodel-core/SKILL.md`](../mathmodel-core/SKILL.md) |

## 边界与分工

- **本技能只管方法与选型**：赛题分析、工作目录与阶段编排在 `mathmodel-core`；论文写作与排版在
  `mathmodel-paper`；数据图表在 `mathmodel-figure`；示意图在 `mathmodel-diagram`；去 AI 与交付校核在
  `mathmodel-deai`；结构自检与评分在 `mathmodel-score`。
- **不编造**：方法出处、参数范围与优缺点判断要有依据；模拟结果不得说成复现了真实结果。
- **不代替判断**：候选与对比表是输入，最终选型由使用者确认（或明确委托代选）。
