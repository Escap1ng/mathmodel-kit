# Figure Template Catalog

Each id maps to a bundled script under `code/templates/`.

| id | script | figure |
| --- | --- | --- |
| `multiclass-shap-combo` | `make_multiclass_shap_combo.py` | 多分类 SHAP 柱状图与蜂群图组合图 |
| `paired-raincloud` | `make_paired_raincloud.py` | 配对云雨图 |
| `cv-roc-ci` | `make_cv_roc_ci.py` | 交叉验证 ROC 曲线与置信区间图 |
| `taylor-diagram` | `make_taylor_diagram.py` | 多模型评价泰勒图 |
| `correlation-pairgrid` | `make_correlation_pairgrid.py` | 数据分布、拟合线、置信区间、相关系数组合图 |
| `prediction-marginal-grid` | `make_prediction_marginal_grid.py` | 预测值与真实值边缘分布组合图 |
| `rf-tpe-surface` | `make_rf_tpe_surface.py` | TPE 优化 RF 模型 3D 曲面图 |
| `grouped-corr-split-violin` | `make_grouped_corr_split_violin.py` | 下三角相关矩阵 + 特征分组与半边小提琴图 |
| `grouped-circular-heatmap` | `make_grouped_circular_heatmap.py` | 分组环形热图 |
| `urban-park-cooling-combo` | `make_urban_park_cooling_combo.py` | 堆叠图 + 云雨图 + 箱线图组合图 |
| `nature-chord-diagram` | `make_nature_chord_diagram.py` | Nature 风格和弦图 |
| `surface-3d` | `make_surface_3d.py` | 三维曲面图（渐变光照 + 底部投影） |
| `heatmap-annotated` | `make_heatmap_annotated.py` | 相关热力图（数值标注 + 上三角遮罩） |
| `fit-conf-residual` | `make_fit_confidence_residual.py` | 拟合对比图（置信带 + 残差子图） |
| `convergence-curve` | `make_convergence_curve.py` | 迭代收敛曲线（种群散点 + 最优/均值线） |
| `pareto-front` | `make_pareto_front.py` | Pareto 前沿图（双目标非支配解集） |
| `line-compare` | `make_line_compare.py` | 性能对比折线图（线型+标记冗余编码） |
| `grouped-bar` | `make_grouped_bar.py` | 分组柱状图（多方案指标对比） |
| `boxplot-jitter` | `make_boxplot_jitter.py` | 箱线图 + 抖动散点（分布与稳定性） |
| `pie-modules` | `make_pie_modules.py` | 模块占比饼图（≤5 类扁平低饱和） |
| `hbar-longlabel` | `make_hbar_longlabel.py` | 长类别条形图（横向柱状替代） |

把用户要的中文图题转成上表之一的 id，然后调用 `code/tools/render_template.py <id>`
（渲染器也接受英文别名与中文图题片段，`--list` 查看全部 id）。
