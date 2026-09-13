# code/style/plot_style.py —— 统一样式模块（保存至工作区 code/，绘图脚本 from plot_style import ... 复用）
# Nature 风格设计系统：颜色只承担三种职责——身份（哪条系列）、方向（升还是降）、层级（主角还是陪衬）；
# 字号、轴线、网格、面板标号、数值标注一律取自本模块常量并调用 style_axes / add_panel_label /
# annotate_bars 等助手，禁止在脚本里另行定义或硬编码色值。规范条文见 docs/guides/visualization-rules.md。
#
# 配色是可替换的：按下列顺序读取主题文件（JSON，契约见 themes/theme.schema.json），下面的颜色常量
# 只是「当前主题」的展开结果，名字与类型保持稳定，脚本照旧 from plot_style import ...。
#   1) 与自身同目录的 theme.json —— 渲染器会写入工作区，改它即可覆盖配色，无需动仓库模板
#   2) 打包内的默认主题 themes/nature.theme.json
#   3) 内置兜底值 _FALLBACK（与 nature 主题逐值一致）
import json
import os
import warnings
from pathlib import Path
import matplotlib
matplotlib.use('Agg')   # 非交互后端：无 GUI 开销，批量出图稳定（交互调试时删除本行）
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap, to_hex, to_rgb

# ===== 主题加载：同目录 theme.json → 打包默认主题 → 内置兜底 =====
# _FALLBACK 与 themes/nature.theme.json 逐值一致，保证主题文件缺失/损坏时行为不变。
_FALLBACK = {
    'main': '#1A6FC4', 'main_light': '#5B9BD5', 'main_pale': '#B4D4F0',
    'accents': ['#E28E2C', '#7B5FD6', '#33B5A5', '#D9544D', '#B89BD9'],
    'baseline': '#767676', 'baseline_dark': '#4D4D4D',
    'positive': '#2E9E44', 'negative': '#E53935',
    'neutral_bg': '#F5F5F5', 'neutral_light': '#D8D8D8', 'neutral_mid': '#A8A8A8',
    'neutral_dark': '#606060', 'ink': '#333333',
    'divergent': ['#1A6FC4', '#F5F5F5', '#D9544D'],
    'sequential': ['#F2F5FA', '#1A6FC4'],
}

_THEME_CANDIDATES = (
    Path(__file__).resolve().with_name('theme.json'),                          # 工作区覆盖（渲染器写入）
    Path(__file__).resolve().parents[2] / 'themes' / 'nature.theme.json',      # 打包默认主题
)


def _read_theme():
    for candidate in _THEME_CANDIDATES:
        try:
            data = json.loads(candidate.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and isinstance(data.get('roles'), dict):
            return data, candidate.name
    return {}, 'builtin'


THEME, THEME_SOURCE = _read_theme()
THEME_NAME = THEME.get('name') if isinstance(THEME.get('name'), str) else 'builtin'


def _theme_str(*keys, fallback):
    """按路径取主题中的字符串色值；缺失或类型不符时回退。"""
    node = THEME
    for key in keys:
        node = node.get(key) if isinstance(node, dict) else None
    return node if isinstance(node, str) and node else fallback


def _theme_list(*keys, fallback):
    """按路径取主题中的色值数组；缺失或类型不符时回退。"""
    node = THEME
    for key in keys:
        node = node.get(key) if isinstance(node, dict) else None
    if isinstance(node, list) and node and all(isinstance(item, str) for item in node):
        return list(node)
    return list(fallback)


def _theme_accent(index, fallback):
    accents = _theme_list('roles', 'identity', 'accents', fallback=_FALLBACK['accents'])
    return accents[index] if index < len(accents) else fallback


# ===== 身份色板（identity）：只回答"这是哪个方法/哪条系列"，跨图含义不变 =====
COLOR_MAIN         = _theme_str('roles', 'identity', 'main', fallback=_FALLBACK['main'])
COLOR_MAIN_LIGHT   = _theme_str('roles', 'identity', 'main_light', fallback=_FALLBACK['main_light'])
COLOR_MAIN_PALE    = _theme_str('roles', 'identity', 'main_pale', fallback=_FALLBACK['main_pale'])
ACCENT_ORANGE      = _theme_accent(0, _FALLBACK['accents'][0])   # 次系列 1
ACCENT_PURPLE      = _theme_accent(1, _FALLBACK['accents'][1])   # 次系列 2
ACCENT_TEAL        = _theme_accent(2, _FALLBACK['accents'][2])   # 次系列 3
ACCENT_CORAL       = _theme_accent(3, _FALLBACK['accents'][3])   # 次系列 4
ACCENT_LAVENDER    = _theme_accent(4, _FALLBACK['accents'][4])   # 次系列 5
IDENTITY_PALETTE = (COLOR_MAIN, ACCENT_ORANGE, ACCENT_PURPLE,
                    ACCENT_TEAL, ACCENT_CORAL, ACCENT_LAVENDER)

# ===== 基准色（baseline）：对照/参考/均值一律中灰，不与主角抢身份 =====
COLOR_BASELINE      = _theme_str('roles', 'baseline', 'base', fallback=_FALLBACK['baseline'])
COLOR_BASELINE_DARK = _theme_str('roles', 'baseline', 'dark', fallback=_FALLBACK['baseline_dark'])

# ===== 方向色（signal）：只用于有正负之分的变化量（差值、增益、损失） =====
COLOR_POSITIVE = _theme_str('roles', 'signal', 'positive', fallback=_FALLBACK['positive'])   # ↑ 提升
COLOR_NEGATIVE = _theme_str('roles', 'signal', 'negative', fallback=_FALLBACK['negative'])   # ↓ 下降

# ===== 中性色（文字、轴线、网格、底色）；禁纯黑 #000000 与纯白描边 =====
NEUTRAL_BG    = _theme_str('roles', 'neutral', 'bg', fallback=_FALLBACK['neutral_bg'])
NEUTRAL_LIGHT = _theme_str('roles', 'neutral', 'light', fallback=_FALLBACK['neutral_light'])
NEUTRAL_MID   = _theme_str('roles', 'neutral', 'mid', fallback=_FALLBACK['neutral_mid'])
NEUTRAL_DARK  = _theme_str('roles', 'neutral', 'dark', fallback=_FALLBACK['neutral_dark'])
COLOR_INK     = _theme_str('roles', 'neutral', 'ink', fallback=_FALLBACK['ink'])

# 明度层级：深=主证据，浅=支持信息（同族降饱和，而不是换色相）
TONE_RAMP = (COLOR_MAIN, COLOR_MAIN_LIGHT, COLOR_MAIN_PALE, NEUTRAL_MID)
# 定性系列一律用身份色＋灰基准，红绿不入系列配色（见「方向色保留」规则）
LINE_PALETTE = [COLOR_MAIN, ACCENT_ORANGE, ACCENT_PURPLE, COLOR_BASELINE]
FILL_ALPHA = 0.15          # 置信带/填充一律淡，不遮数据
HATCH_SEQUENCE = ('', '---', '|||')   # 可选纹理：无/横线/竖线（基础图表不默认斜线圆点）

# 兼容别名：旧脚本里"红=负面、绿=正向、橙=强调、灰=基准"的角色映射保持不变，
# 值已随主题变化；新代码请直接使用上面的语义常量。
COLOR_ACCENT  = COLOR_NEGATIVE
COLOR_SAGE    = COLOR_POSITIVE
COLOR_MUSTARD = ACCENT_ORANGE
COLOR_ROCK    = COLOR_BASELINE

# ===== 字号与线宽（Nature 版式：小字、细线、多留白） =====
FS_TITLE, FS_LABEL, FS_TICK, FS_LEGEND, FS_ANNOT, FS_PANEL = 10.5, 9.5, 8.5, 8.5, 8.0, 12.0
AX_LINEW, TICK_LEN, TICK_PAD = 0.7, 3.2, 3.0
GRID_LINESTYLE = (0, (4, 3))   # 浅灰细虚线，只保留数值轴方向

# ===== 色图（端点来自主题，保证跨图色彩一致） =====
def _build_cmap(cmap_name, stops):
    n = len(stops)
    return LinearSegmentedColormap.from_list(
        cmap_name, [(i / (n - 1), color) for i, color in enumerate(stops)])


DIVERGENT_CMAP = _build_cmap(
    f'{THEME_NAME}_div', _theme_list('cmaps', 'divergent', fallback=_FALLBACK['divergent']))
SURFACE_CMAP = DIVERGENT_CMAP                        # 与 DIVERGENT_CMAP 同一色图，供发散型曲面使用
SEQUENTIAL_CMAP = _build_cmap(                       # 黑白打印/单极数据变体
    f'{THEME_NAME}_seq', _theme_list('cmaps', 'sequential', fallback=_FALLBACK['sequential']))

# ===== 标准尺寸（A4 版心 16cm ≈ 6.3in；Nature 单栏 89mm ≈ 3.5in） =====
FIG_FULL = (6.3, 4.0)     # 整版宽图（折线、柱状、条形）
FIG_TALL = (6.3, 5.5)     # 双子图竖版（拟合+残差等）
FIG_SQUARE = (5.6, 4.6)   # 近方形（热图、环图、散点方阵）

# ===== 字体检测回退（按安装情况过滤字体栈，缺字体环境避免方框与 findfont 刷屏） =====
_INSTALLED_FONTS = {f.name for f in font_manager.fontManager.ttflist}

def pick_cjk_font(candidates=('Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei')):
    for name in candidates:
        if name in _INSTALLED_FONTS:
            return name
    warnings.warn('未找到任何中文字体，图中中文将显示为方框！请安装 Microsoft YaHei 或 Noto Sans CJK。')
    return 'sans-serif'

def pick_font_stack(latin=('Arial', 'Helvetica', 'Liberation Sans')):
    """西文候选只保留已安装的字体，再补 DejaVu Sans 兜底符号与中文字体。"""
    stack = [name for name in latin if name in _INSTALLED_FONTS]
    stack += ['DejaVu Sans', pick_cjk_font()]
    return stack

def identity_color(i):
    """按序取身份色：第 0 个恒为主角蓝，其后为橙/紫/青/珊红/淡紫，超出后循环。"""
    return IDENTITY_PALETTE[i % len(IDENTITY_PALETTE)]

def tint(color, amount=0.35):
    """向白混合以降低饱和/体现层级（amount=0 原色，1 纯白）。用于同族明度阶梯。"""
    r, g, b = to_rgb(color)
    return to_hex((r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount))

def delta_annotation(base, value, digits=0):
    """相对基准的有向变化 → (文本, 颜色)：↑绿 ↓红，仅用于真正表达增降的场合。"""
    if base == 0:
        return '—', COLOR_BASELINE
    pct = (value - base) / abs(base) * 100
    arrow, color = (('↑', COLOR_POSITIVE) if pct > 0
                    else ('↓', COLOR_NEGATIVE) if pct < 0
                    else ('=', COLOR_BASELINE))
    return f'{arrow}{abs(pct):.{digits}f}%', color

def style_axes(ax, grid='y'):
    """Nature 式坐标框架：去上/右 spine、细轴线外伸刻度、仅保留单向浅灰细网格。"""
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_linewidth(AX_LINEW)
        ax.spines[side].set_color(NEUTRAL_DARK)
    ax.tick_params(axis='both', which='both', direction='out', length=TICK_LEN,
                   width=AX_LINEW, color=NEUTRAL_DARK, colors=COLOR_INK,
                   labelsize=FS_TICK, pad=TICK_PAD)
    for axis in (ax.xaxis, ax.yaxis):
        axis.label.set_fontsize(FS_LABEL)
        axis.label.set_color(COLOR_INK)
    if grid in ('x', 'y', 'both'):
        ax.grid(axis=grid, color=NEUTRAL_LIGHT, linewidth=0.6, linestyle=GRID_LINESTYLE)
        ax.set_axisbelow(True)
    return ax

def add_panel_label(ax, label, x=-0.11, y=1.02, fontsize=FS_PANEL):
    """多子图左下角面板标号（Nature 粗体小写字母，压在轴框外左上）。"""
    ax.text(x, y, label, transform=ax.transAxes, fontsize=fontsize,
            fontweight='bold', color=COLOR_INK, va='bottom', ha='left')
    return ax

def annotate_bars(ax, bars, fmt='{:.2f}', orient='v', fontsize=FS_ANNOT, color=NEUTRAL_DARK):
    """柱/条端数值标注：偏移量按当前轴范围自适应，负值自动换到下方，字号小且深灰不抢数据。"""
    lo, hi = (ax.get_ylim() if orient == 'v' else ax.get_xlim())
    step = (hi - lo) * 0.015
    for bar in bars:
        if orient == 'v':
            value, x, y = bar.get_height(), bar.get_x() + bar.get_width() / 2, bar.get_height()
            y += step if value >= 0 else -step
            ax.text(x, y, fmt.format(value), ha='center',
                    va='bottom' if value >= 0 else 'top', fontsize=fontsize, color=color)
        else:
            value = bar.get_width()
            x = bar.get_width() + (step if value >= 0 else -step)
            y = bar.get_y() + bar.get_height() / 2
            ax.text(x, y, fmt.format(value), va='center',
                    ha='left' if value >= 0 else 'right', fontsize=fontsize, color=color)
    return ax

def apply_style():
    # font.family 必须传具体字体名列表：matplotlib 的字形回退（3.6+）只在 family 为
    # 多字体列表时生效——逐字体查找缺失字形。若用 'sans-serif' 别名，findfont 只取
    # font.sans-serif 里第一个可用字体，中文缺字形时不会回退到列表后续字体（直接方框）。
    # 栈顺序：Arial 等西文无衬线（Nature 版式）→ DejaVu Sans 兜底符号 → 中文黑体系；
    # 未安装的候选由 pick_font_stack 先过滤掉，免得渲染时刷屏 findfont 警告。
    sns.set_theme(style='ticks', palette=LINE_PALETTE, font_scale=1.0,
                  rc={'axes.axisbelow': True, 'axes.edgecolor': NEUTRAL_DARK,
                      'axes.labelcolor': COLOR_INK, 'axes.spines.top': False,
                      'axes.spines.right': False, 'xtick.color': COLOR_INK,
                      'ytick.color': COLOR_INK, 'figure.frameon': False})
    plt.rcParams.update({          # 覆盖顺序：set_theme 在前，微调在后
        'font.family': pick_font_stack(),
        'axes.unicode_minus': False,
        'svg.fonttype': 'none',   # SVG 中文字保留为可编辑文本（与 rf-tpe-surface 一致）
        'pdf.fonttype': 42,       # PDF 嵌入 TrueType 字体，便于排版软件编辑
        'figure.dpi': 100,         # 仅影响屏幕交互渲染速度；存图一律 savefig.dpi，与正式版同品质
        'savefig.dpi': 300,        # 输出出版级分辨率（预览与正式同品质）
        'savefig.facecolor': 'white',
        'font.size': FS_LABEL,
        'axes.titlesize': FS_TITLE,
        'axes.titleweight': 'bold',
        'axes.titlecolor': COLOR_INK,
        'axes.titlepad': 10,
        'axes.labelsize': FS_LABEL,
        'axes.linewidth': AX_LINEW,
        'xtick.labelsize': FS_TICK,
        'ytick.labelsize': FS_TICK,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': TICK_LEN,
        'ytick.major.size': TICK_LEN,
        'legend.fontsize': FS_LEGEND,
        'legend.frameon': False,   # 图例不带框：默认减噪，需要遮底时由脚本显式覆写
        'legend.handlelength': 1.8,
        'legend.borderaxespad': 0.4,
        'lines.markersize': 4.5,
        'patch.linewidth': 0.8,
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
