# 实现指南

方法选型见 [selection-guide.md](selection-guide.md)，方法清单见 [method-library.md](method-library.md)。
本文件给出推荐库、最小可运行骨架与实现纪律。

## 一、总体原则

有成熟库的方法优先调用，禁止手动重复实现已有算法；自写代码集中于无现成实现的方法
（评价赋权、灰色预测、仿真框架等）。需单独安装的库先在环境预检中确认可用性，
安装失败时退化为等价替代方法，并在论文中说明。

## 二、方法类别 → 推荐实现

| 算法 / 方法类别 | 推荐实现 |
|---|---|
| 线性规划 / 0-1 整数规划 / 混合整数 | `pulp`（自带 CBC 求解器）或 `scipy.optimize.milp`；不手写单纯形法 |
| 非线性 / 约束优化 | `scipy.optimize.minimize`（SLSQP / trust-constr）；凸问题用 `cvxpy` |
| 连续全局优化 | `scipy.optimize.differential_evolution`（差分进化）、`dual_annealing`（模拟退火） |
| 组合启发式（GA / SA / PSO 等） | 自行实现，编码与算子须贴合问题；指派 / TSP 可用 `python-ortools` |
| 多目标优化（NSGA-II/III） | `pymoo`（需单独安装） |
| 微分方程数值解 | `scipy.integrate.solve_ivp`（自动选 RK45/BDF）；手写 RK4 仅作原理演示 |
| 图论（最短路 / 生成树 / 最大流 / 匹配） | `networkx`；大规模稀疏图用 `scipy.sparse.csgraph` |
| 插值与拟合 | `scipy.interpolate`（CubicSpline / interp1d）、`numpy.polyfit` |
| 统计检验与相关性 | `scipy.stats`（ttest_ind、chi2_contingency、spearmanr、shapiro） |
| 回归分析 | 统计推断用 `statsmodels`（提供 p 值 / 置信区间）；纯预测用 `sklearn` |
| 时间序列 | `statsmodels`（ARIMA、ExponentialSmoothing）；Prophet 需单独安装 `prophet` |
| 机器学习（分类 / 聚类 / 降维） | `scikit-learn`；梯度提升树用 `xgboost` / `lightgbm` |
| 灰色预测 GM(1,1) / 马尔可夫链 | 自写（累加生成 + 最小二乘参数估计 + 后验差检验 C/P） |
| 熵权法 / TOPSIS / AHP / 灰色关联 / 模糊综合评价 | 自写（矩阵标准化 + 赋权公式），注意负向指标标准化方向 |
| 仿真（蒙特卡洛 / 离散事件 / 排队 / 元胞自动机） | `numpy.random` + 自写事件驱动框架 |
| 信号处理 | `numpy.fft`（FFT）、`pywt`（小波，需单独安装） |

## 三、最小可运行骨架

### 3.1 遗传算法（GA）

关键参数为启发式算法文献的经验范围，须按问题规模与解空间特点调整，并在论文中说明取值依据。

```python
# 参数：按问题规模调整，并在论文中给出取值依据
POP_SIZE = 120          # 种群规模：100-200
MAX_GEN = 150           # 最大迭代：100-200
CROSS_RATE = 0.85       # 交叉率：0.8-0.9
MUT_RATE = 0.05         # 变异率：0.01-0.15（连续优化常用低端，组合优化可用高端）
ELITE_RATE = 0.08       # 精英保留：5%-10%
```

**必须包含**：智能初始化策略、自适应变异、重启机制、精英保留。

**输出要求**：迭代收敛曲线图、最优解决策变量表、与基准方案对比（提升百分比）。

### 3.2 模拟退火（SA）

```python
T0 = 1000               # 初始温度
T_MIN = 1e-8            # 终止温度
COOLING_RATE = 0.95     # 冷却系数：0.9-0.99
ITER_PER_TEMP = 100     # 每温度迭代次数
```

### 3.3 0-1 整数规划

```python
import pulp

prob = pulp.LpProblem("Problem_Name", pulp.LpMaximize)
x1 = pulp.LpVariable("x1", cat='Binary')
x2 = pulp.LpVariable("x2", cat='Binary')
# 目标函数示例：最大化利润
prob += profit_per_unit * x1 + profit_per_unit2 * x2
# 约束条件示例
prob += cost_per_unit * x1 + cost_per_unit2 * x2 <= budget
prob.solve()
```

### 3.4 统一数据加载入口

```python
import os
import fitz  # PyMuPDF
import openpyxl
import pandas as pd

def load_data(file_path):
    """统一数据加载入口"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return read_pdf(file_path)
    elif ext in ('.xlsx', '.xls'):
        return read_excel(file_path)
    else:
        raise ValueError(f"不支持的数据格式: {ext}")

def read_pdf(file_path):
    """使用 PyMuPDF 读取 PDF 文本"""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def read_excel(file_path):
    """使用 pandas 读取 Excel：openpyxl 仅支持 .xlsx/.xlsm，旧版 .xls 必须用 xlrd 引擎"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.xls':
        return pd.read_excel(file_path, engine='xlrd')   # 需 pip install xlrd
    return pd.read_excel(file_path, engine='openpyxl')
```

## 四、实现纪律

- 代码完整可运行，关键参数以注释说明取值依据，输出清晰的结果摘要；
- 中间结果从简，核心结果用表格 / 图形呈现并配文字解读；
- 按 [selection-guide.md](selection-guide.md) 第五节选择验证手段，验证结果一并落盘；
- 结果不正确、不合理或误差大时，分析原因并修正模型 / 算法后重新验证，形成闭环。

## 五、与其他技能的分工

| 需求 | 交给哪个技能 |
|---|---|
| 论文正文写作、LaTeX 排版、PDF/Word 输出 | `mathmodel-paper` |
| 数据图表（模板库内外） | `mathmodel-figure` |
| 技术路线图 / 流程图 / 问题分析图 | `mathmodel-diagram` |
| 去 AI 化与零宽字符清理 | `mathmodel-deai` |
| 章节结构自检与百分制评分 | `mathmodel-score` |
| 阶段编排、工作目录与赛题分析 | `mathmodel-core` |

Word 版式后处理的角色边界（由 pandoc 生成、仅调样式不重建内容）与执行命令，见
[`mathmodel-paper/SKILL.md`](../../mathmodel-paper/SKILL.md) 与主技能阶段五。
