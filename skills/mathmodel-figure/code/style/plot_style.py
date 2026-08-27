# code/style/plot_style.py —— 统一样式模块（保存至工作区 code/，绘图脚本 from plot_style import * 复用）
# 提取自 math-modeling-helper 主技能第 4 章；色板/纹理/标准尺寸的唯一定义，禁止在脚本中另行定义。
import os
import warnings
import matplotlib
matplotlib.use('Agg')   # 非交互后端：无 GUI 开销，批量出图稳定（交互调试时删除本行）
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager

# ===== Master Palette（coolwarm 学术色板，与可视化规范配色方案一致；禁纯黑 #000000） =====
COLOR_MAIN    = '#3B4CC0'   # 主色A coolwarm蓝：核心数据/模型结果
COLOR_ACCENT  = '#B40426'   # 辅色B coolwarm红：对比/误差/负面
COLOR_SAGE    = '#55A868'   # 辅色C 苔绿：辅助/正向
COLOR_MUSTARD = '#DD8452'   # 辅色D 赭橙：强调/极值
COLOR_ROCK    = '#8E9AAF'   # 中性色E 岩石灰：基准/背景
COLOR_INK     = '#2F353B'   # 深色F 炭墨黑：文字/轴线/边框
LINE_PALETTE = [COLOR_MAIN, COLOR_ACCENT, COLOR_SAGE, COLOR_ROCK]
FILL_ALPHA = 0.2
HATCH_SEQUENCE = ['', '---', '|||']   # 可选纹理：无/横线/竖线（基础图表不默认斜线圆点）
DIVERGENT_CMAP = plt.get_cmap('coolwarm')   # 蓝→灰白→红（热力图/发散数据，与 rf-tpe-surface 同款）
SURFACE_CMAP   = DIVERGENT_CMAP             # 与 DIVERGENT_CMAP 同一色图，供 3D 曲面/热力图使用
FIG_FULL = (6.3, 4.0)   # 整版宽图（A4 版心 16cm ≈ 6.3in）
FIG_TALL = (6.3, 5.5)   # 双子图竖版（拟合+残差等）

# ===== 中文字体检测回退（缺字体环境避免静默输出方框） =====
def pick_cjk_font(candidates=('SimHei', 'Microsoft YaHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei')):
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            return name
    warnings.warn('未找到任何中文字体，图中中文将显示为方框！请安装 SimHei 或 Noto Sans CJK。')
    return 'sans-serif'

def pick_cjk_serif(candidates=('SimSun', 'NSimSun', 'Songti SC', 'Noto Serif CJK SC', 'STSong')):
    # 中文优先衬线（宋体族）以匹配 Times New Roman；全缺时回退无衬线中文字体（沿用上方告警）
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            return name
    return pick_cjk_font()

def apply_style():
    # font.family 必须传具体字体名列表：matplotlib 的字形回退（3.6+）只在 family 为
    # 多字体列表时生效——逐字体查找缺失字形。若用 'serif' 别名，findfont 只取
    # font.serif 里第一个可用字体，中文缺字形时不会回退到列表后续字体（直接方框）。
    # 顺序：Times 覆盖西文/数字 → DejaVu Serif 兜底符号 → 中文衬线（缺时回退无衬线并告警）。
    sns.set_theme(style='ticks', palette=LINE_PALETTE, font_scale=1.1,
                  rc={'axes.axisbelow': True, 'axes.edgecolor': COLOR_INK,
                      'axes.labelcolor': COLOR_INK, 'axes.spines.top': False,
                      'axes.spines.right': False, 'xtick.color': COLOR_INK,
                      'ytick.color': COLOR_INK, 'figure.frameon': False})
    plt.rcParams.update({          # 覆盖顺序：set_theme 在前，微调在后
        'font.family': ['Times New Roman', 'DejaVu Serif', pick_cjk_serif()],
        'axes.unicode_minus': False,
        'svg.fonttype': 'none',   # SVG 中文字保留为可编辑文本（与 rf-tpe-surface 一致）
        'pdf.fonttype': 42,       # PDF 嵌入 TrueType 字体，便于排版软件编辑
        'figure.dpi': 100,         # 仅影响屏幕交互渲染速度；存图一律 savefig.dpi，与正式版同品质
        'savefig.dpi': 300,        # 输出出版级分辨率（预览与正式同品质）
        'font.size': 11,
        'axes.linewidth': 0.8,
    })

def save_fig(fig, path, vector=False, close=True, dpi=300):
    """统一保存入口：默认位图 300DPI + 防裁切（PNG 无损压缩，体积约降 10–30%）；
    可选同步导出 PDF 矢量版；默认保存后关闭释放内存（close 后 figure 不可再编辑）"""
    # 目录自愈：figures/final 等输出目录不存在时自动创建，避免 FileNotFoundError
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.1,
                pil_kwargs={'optimize': True} if path.rsplit('.', 1)[-1].lower()
                in ('png', 'jpg', 'jpeg', 'gif', 'webp', 'tif', 'tiff') else None)
    if vector:
        fig.savefig(path.rsplit('.', 1)[0] + '.pdf', bbox_inches='tight')
    if close:
        plt.close(fig)
# 分级 DPI 说明：线条/柱状类优先 vector=True（PDF 矢量，体积小）；位图密度类
# （hexbin/大规模散点/3D曲面）可传 dpi=200；仅精细细节图（热力图小格标注）保持 300

apply_style()   # import 即完成一次性初始化
