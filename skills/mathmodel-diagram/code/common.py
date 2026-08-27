#!/usr/bin/env python3
"""common.py — mathmodel-diagram 的 matplotlib 绘图基元层。

坐标系约定
----------
`setup_canvas(w_px, h_px)` 建一张 1 px = 0.01 inch（逻辑 100 dpi）的画布，
并把 y 轴翻转为**向下增长**（`ax.set_ylim(h_px, 0)`）。因此 drawio 时代逐像素
标定出来的几何常量（x/y/w/h、步距、槽宽）可以原值复用，不必换算。

单位换算
--------
matplotlib 的字号与线宽以 pt 计，本模块所有对外参数一律用 **px**，内部按
`PX2PT = 0.72` 换算（1 px @100dpi = 0.72 pt）。字宽模型仍是 px：
CJK/全角 = 字号 px，半角 = 字号/2，行高 = 字号 + 3（见 `text_width`）。

用法
----
模板脚本只跟两样东西打交道：`Recorder`（把绘图指令排队，等画布尺寸定下来后一次
回放，用于高度自适应的模板）与 `draw_*` 基元（已知画布尺寸时可直接画）。
"""
from __future__ import annotations

import pathlib
import sys
import unicodedata
from math import hypot

import numpy as np
import matplotlib as mpl

mpl.use("Agg")

from matplotlib.colors import LinearSegmentedColormap, to_rgba  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Ellipse, FancyBboxPatch, PathPatch, Polygon, Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402

mpl.rcParams["pdf.fonttype"] = 42      # PDF 里的中文保持可编辑文本，不退化成曲线
mpl.rcParams["ps.fonttype"] = 42
mpl.rcParams["hatch.linewidth"] = 0.8
mpl.rcParams["axes.unicode_minus"] = False

# 1 px（100 dpi 逻辑）= 0.72 pt
PX2PT = 0.72
DPI = 100.0
OUT_DPI = 300.0

DASH = (0, (3, 3))     # 分组框 / 次要数据流
DOT = (0, (1, 3))      # 分带线
INK = "#2F353B"        # 炭墨：正文与主流程箭头

# 探测顺序：Windows → Windows(alt) → Linux(思源/黑体) → Linux(文泉驿)
CJK_FONTS = ("SimHei", "Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans SC",
             "WenQuanYi Micro Hei", "Source Han Sans SC")
_FONT: str | None = None


# --------------------------------------------------------------- 字体与画布
def pick_cjk_font(quiet: bool = False) -> str | None:
    """按 `CJK_FONTS` 顺序挑一个系统里真装了的中文字体，设进 rcParams。

    一个都没有时只 warn 并返回 None——中文会渲染成方框，这必须让人看见，
    但不能因此让脚本崩掉（`--check` 模式压根不需要字体）。
    """
    global _FONT
    if _FONT is not None:
        return _FONT
    from matplotlib import font_manager

    avail = {f.name for f in font_manager.fontManager.ttflist}
    for name in CJK_FONTS:
        if name in avail:
            # font.family 给成"列表"才会启用 matplotlib 的字形回退：中文走 CJK 字体，
            # SimHei 缺的 −、₁、² 之类符号自动落到后面的字体，不会渲染成方框。
            rest = [f for f in CJK_FONTS + ("DejaVu Sans",) if f != name and f in avail]
            if "DejaVu Sans" not in rest:
                rest.append("DejaVu Sans")
            mpl.rcParams["font.family"] = [name] + rest
            mpl.rcParams["font.sans-serif"] = [name] + rest
            _FONT = name
            return name
    if not quiet:
        print(f"⚠ 未找到任何中文字体（试过的：{'、'.join(CJK_FONTS)}）；"
              f"渲染结果里的中文会变成方框，请安装 SimHei / Noto Sans CJK SC 后重跑",
              file=sys.stderr)
    return None


def pt(fs_px: float) -> float:
    """px 字号 → pt 字号。"""
    return float(fs_px) * PX2PT


def radius_of(w: float, h: float, arc: float) -> float:
    """drawio 的 `arcSize`（占短边百分比）→ 圆角半径 px。arc=50 即胶囊。"""
    return min(w, h) * arc / 100.0 if arc else 0.0


def lw(width_px: float) -> float:
    """px 描边宽度 → pt 线宽。"""
    return max(float(width_px), 0.1) * PX2PT


def setup_canvas(w_px: float, h_px: float, facecolor: str = "white"):
    """建画布：1 px = 0.01 inch，坐标原点在左上、y 轴向下。返回 (fig, ax)。"""
    fig = Figure(figsize=(w_px / DPI, h_px / DPI), dpi=DPI)
    fig.patch.set_facecolor(facecolor)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, w_px)
    ax.set_ylim(h_px, 0)          # y 轴向下，与像素栅格一致
    ax.axis("off")
    ax.set_facecolor(facecolor)
    return fig, ax


def save_figure(fig, out_path) -> tuple[pathlib.Path, pathlib.Path]:
    """存 PNG（300 dpi）+ 同名矢量 PDF。返回两个路径。"""
    out = pathlib.Path(out_path)
    if out.parent and not out.parent.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
    png = out.with_suffix(".png")
    pdf = out.with_suffix(".pdf")
    facecolor = fig.get_facecolor()
    fig.savefig(png, dpi=OUT_DPI, facecolor=facecolor)
    fig.savefig(pdf, facecolor=facecolor)
    return png, pdf


# --------------------------------------------------------------- 字宽与校验
def text_width(text: str, font_size: float) -> float:
    """一行文字的像素宽度：CJK/全角 = 字号，半角（含空格）= 字号/2。"""
    return sum(font_size if unicodedata.east_asian_width(c) in ("W", "F")
               else font_size / 2 for c in str(text))


def check_text_fits(text: str, box_w: float, font_size: float, pad: float = 8.0):
    """按 "\\n" 分行逐行判是否放得下。返回 (ok, 最宽行所需 px)。

    `pad` 是盒子两侧合计预留的内边距（默认 8 px，与各模板历史口径一致）。
    """
    lines = str(text).split("\n")
    need = max((text_width(ln, font_size) for ln in lines), default=0.0)
    return need <= max(float(box_w) - pad, 0.0), need


def lines_of(value):
    """接受 "a\\nb"、["a","b"]、None → 行列表。"""
    if value is None:
        return [""]
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return str(value).split("\n")


def stack(value) -> str:
    """竖排文字 = 逐字 "\\n" 堆叠（字符保持正立，不是整体旋转 90°）。"""
    return "\n".join(list(str(value)))


def slots(a: float, b: float, n: int, gap: float):
    """把区间 [a, b] 等分成 n 个槽，槽间留 `gap`。返回 [(起点, 尺寸)]。

    数量可变的同族元素一律用它算坐标，不要手算每个盒子。
    """
    size = (b - a - (n - 1) * gap) / n
    return [(a + i * (size + gap), size) for i in range(n)]


# --------------------------------------------------------------- 内部工具
def _boxstyle(radius: float, w: float, h: float):
    r = min(float(radius), w / 2.0, h / 2.0)
    if r <= 0.35:
        return "square,pad=0"
    return f"round,pad=0,rounding_size={r:g}"


def _gradient(ax, patch, x, y, w, h, c1, c2, vertical: bool = False, z: float = 2.0):
    """把水平（或垂直）两段渐变垫在 patch 里，用来复刻 drawio 的 gradientColor。"""
    n = 96
    ramp = np.linspace(0.0, 1.0, n).reshape(1, n) if not vertical else \
        np.linspace(0.0, 1.0, n).reshape(n, 1)
    cmap = LinearSegmentedColormap.from_list("g", [to_rgba(c1), to_rgba(c2)])
    im = ax.imshow(ramp, cmap=cmap, aspect="auto", interpolation="bilinear", zorder=z + 0.1,
                   extent=[x, x + w, y + h, y] if not vertical else [x, x + w, y + h, y])
    im.set_clip_path(patch)
    return im


def _place(x, y, w, h, halign, valign, text, fs, pad):
    """由盒子的对齐方式算出 ax.text 的锚点（y 轴向下，故手工算块高）。"""
    nlines = max(text.count("\n") + 1, 1)
    block_h = nlines * (fs + 3)
    cx = {"left": x + pad, "right": x + w - pad}.get(halign, x + w / 2)
    if valign == "top":
        cy = y + pad + block_h / 2
    elif valign == "bottom":
        cy = y + h - pad - block_h / 2
    else:
        cy = y + h / 2
    return cx, cy


def _put_text(ax, x, y, w, h, text, fs, fc, bold, halign, valign, z, pad=4.0, alpha=1.0,
              dx=0.0, dy=0.0):
    if text in (None, ""):
        return
    s = str(text)
    cx, cy = _place(x, y, w, h, halign, valign, s, fs, pad)
    ax.text(cx + dx, cy + dy, s, fontsize=pt(fs), color=fc, alpha=alpha,
            fontweight="bold" if bold else "normal",
            ha={"left": "left", "right": "right"}.get(halign, "center"), va="center",
            linespacing=(fs + 3) / fs if "\n" in s else 1.0, zorder=z + 1)


# --------------------------------------------------------------- 绘图基元
def draw_box(ax, x, y, w, h, text=None, fill="#ffffff", stroke="#333333", width=1.0,
             ls=None, fs=16, fc=INK, bold=True, radius=0.0, halign="center",
             valign="middle", z=2.0, grad=None, pad=4.0, alpha=1.0):
    """圆角（`radius`>0，单位 px）或直角盒，可选渐变填充与盒内文字。

    `fill=None` / `stroke=None` 表示无填充 / 无描边（纯文字或色块时用）。
    """
    patch = FancyBboxPatch((x, y), w, h, boxstyle=_boxstyle(radius, w, h),
                           linewidth=lw(width) if stroke else 0,
                           edgecolor=stroke or "none", linestyle=ls or "solid",
                           facecolor=fill if (fill and not grad) else "none",
                           alpha=alpha, zorder=z)
    ax.add_patch(patch)
    if grad:
        _gradient(ax, patch, x, y, w, h, grad[0], grad[1], z=z)
    _put_text(ax, x, y, w, h, text, fs, fc, bold, halign, valign, z, pad, alpha)
    return patch


def draw_rect(ax, x, y, w, h, fill="#ffffff", stroke=None, width=1.0, ls=None,
              text=None, fs=16, fc=INK, bold=True, halign="center", valign="middle",
              z=2.0, grad=None, pad=4.0, alpha=1.0):
    """直角矩形（色块、面板底、无边框背景用）。"""
    patch = Rectangle((x, y), w, h, linewidth=lw(width) if stroke else 0,
                      edgecolor=stroke or "none", linestyle=ls or "solid",
                      facecolor=fill if (fill and not grad) else "none",
                      alpha=alpha, zorder=z)
    ax.add_patch(patch)
    if grad:
        _gradient(ax, patch, x, y, w, h, grad[0], grad[1], z=z)
    _put_text(ax, x, y, w, h, text, fs, fc, bold, halign, valign, z, pad, alpha)
    return patch


def draw_text(ax, x, y, w, h, text, fs=16, fc=INK, bold=True, halign="center",
              valign="middle", z=2.0, pad=2.0, alpha=1.0):
    """无边框文字（栏外标签、说明文字、虚线框标题用）。"""
    _put_text(ax, x, y, w, h, text, fs, fc, bold, halign, valign, z, pad, alpha)


def draw_dashed_rect(ax, x, y, w, h, color="#5a5a5a", width=1.0, ls=DASH, z=2.0):
    """虚线分组框（点线传 `ls=DOT`）。"""
    ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor=color,
                           linewidth=lw(width), linestyle=ls, zorder=z))


def draw_polygon(ax, pts, fill="#ffffff", stroke="#333333", width=1.0, ls=None,
                 text=None, fs=16, fc=INK, bold=True, z=2.0, grad=None,
                 halign="center", valign="middle", pad=2.0, alpha=1.0):
    """任意多边形（旗标、菱形、六边形、块箭头都基于它）。"""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    patch = Polygon(pts, closed=True, linewidth=lw(width) if stroke else 0,
                    edgecolor=stroke or "none", linestyle=ls or "solid",
                    facecolor=fill if (fill and not grad) else "none",
                    joinstyle="round", alpha=alpha, zorder=z)
    ax.add_patch(patch)
    if grad:
        _gradient(ax, patch, min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys),
                  grad[0], grad[1], z=z)
    _put_text(ax, min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys),
              text, fs, fc, bold, halign, valign, z, pad, alpha)
    return patch


def draw_flag(ax, x, y, w, h, text=None, fill="#b6d8f6", stroke="#5b93bd", width=1.0,
              tip=0.22, fs=16, fc=INK, bold=True, z=2.0, grad=None, text_dx=0.0):
    """右向五边形旗标：`tip` = 箭头尖深度占宽的比例（对应 drawio 的 arrowSize）。

    文字落在去掉箭尖后的矩形段中心，`text_dx` 用于再微调（对应 spacingRight）。
    """
    d = min(max(tip, 0.0), 0.9) * w
    pts = [(x, y), (x + w - d, y), (x + w, y + h / 2), (x + w - d, y + h), (x, y + h)]
    patch = draw_polygon(ax, pts, fill, stroke, width, None, None, fs, fc, bold, z, grad)
    if text not in (None, ""):
        _put_text(ax, x, y, w - d, h, text, fs, fc, bold, "center", "middle", z, 2.0,
                  dx=text_dx)
    return patch


def draw_block_arrow(ax, x, y, w, h, direction="east", fill="#4874cc", stroke=None,
                     width=1.0, shaft=0.62, head=0.4, text=None, fs=16, fc=INK,
                     bold=True, z=2.0, grad=None, halign="center", valign="middle",
                     pad=2.0):
    """粗块箭头（阶段推进）。`shaft` = 杆厚占截面的比例，`head` = 头长占长度/高度的比例。"""
    s = min(max(shaft, 0.05), 1.0)

    def east():
        hl = min(head, 0.9) * w
        t = s * h
        y0, y1 = y + (h - t) / 2, y + (h + t) / 2
        return [(x, y0), (x + w - hl, y0), (x + w - hl, y), (x + w, y + h / 2),
                (x + w - hl, y + h), (x + w - hl, y1), (x, y1)]

    def south():
        hl = min(head, 0.9) * h
        t = s * w
        x0, x1 = x + (w - t) / 2, x + (w + t) / 2
        return [(x0, y), (x1, y), (x1, y + h - hl), (x + w, y + h - hl),
                (x + w / 2, y + h), (x, y + h - hl), (x0, y + h - hl)]

    def west():
        hl = min(head, 0.9) * w
        t = s * h
        y0, y1 = y + (h - t) / 2, y + (h + t) / 2
        return [(x + w, y0), (x + hl, y0), (x + hl, y), (x, y + h / 2),
                (x + hl, y + h), (x + hl, y1), (x + w, y1)]

    def north():
        hl = min(head, 0.9) * h
        t = s * w
        x0, x1 = x + (w - t) / 2, x + (w + t) / 2
        return [(x0, y + h), (x1, y + h), (x1, y + hl), (x + w, y + hl),
                (x + w / 2, y), (x, y + hl), (x0, y + hl)]

    pts = {"east": east, "south": south, "west": west, "north": north}[direction]
    return draw_polygon(ax, pts(), fill, stroke, width, None, text, fs, fc, bold, z,
                        grad, halign, valign, pad)


def draw_double_arrow(ax, x, y, w, h, fill="#d9d9d9", stroke="#9a9a9a", width=1.0,
                      shaft=0.4, head=0.28, text=None, fs=16, fc=INK, bold=True, z=2.0):
    """双向块箭头（互相印证 / 对照关系）。"""
    t = shaft * h
    hl = head * w
    y0, y1 = y + (h - t) / 2, y + (h + t) / 2
    pts = [(x + hl, y0), (x + w - hl, y0), (x + w - hl, y), (x + w, y + h / 2),
           (x + w - hl, y + h), (x + w - hl, y1), (x + hl, y1), (x + hl, y + h),
           (x, y + h / 2), (x + hl, y)]
    return draw_polygon(ax, pts, fill, stroke, width, None, text, fs, fc, bold, z)


def draw_diamond(ax, x, y, w, h, text=None, fill="#ffffff", stroke="#333333", width=1.2,
                 fs=16, fc=INK, bold=True, z=2.0):
    """菱形（判定）。"""
    pts = [(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)]
    return draw_polygon(ax, pts, fill, stroke, width, None, text, fs, fc, bold, z)


def draw_hexagon(ax, x, y, w, h, text=None, fill="#bae2e4", stroke="#4f8f8b", width=1.0,
                 size=12, fs=16, fc=INK, bold=True, z=2.0):
    """左右各切一角的六边形；`size` 是切角深度（px，对应 drawio 的 fixedSize size）。"""
    d = min(size, w / 2)
    pts = [(x + d, y), (x + w - d, y), (x + w, y + h / 2), (x + w - d, y + h),
           (x + d, y + h), (x, y + h / 2)]
    return draw_polygon(ax, pts, fill, stroke, width, None, text, fs, fc, bold, z)


def draw_cylinder(ax, x, y, w, h, text=None, fill="#e6e9f8", stroke="#9a96c0",
                  width=1.2, ratio=0.32, fs=16, fc=INK, bold=True, z=2.0, grad=None):
    """圆柱（数据库 / 中转标签）。上椭圆 + 矩形身 + 下椭圆，文字居中。"""
    eh = min(ratio * w, h / 3)
    body = Rectangle((x, y + eh / 2), w, h - eh,
                     linewidth=0, facecolor=grad[0] if grad else fill, zorder=z)
    ax.add_patch(body)
    if grad:
        _gradient(ax, body, x, y, w, h, grad[0], grad[1], z=z)
    # 侧边与底弧
    ax.add_patch(PathPatch(
        Path([(x, y + eh / 2), (x, y + h - eh / 2),
              (x, y + h - eh / 2 + eh * 0.28), (x + w / 2, y + h),
              (x + w, y + h - eh / 2 + eh * 0.28), (x + w, y + h - eh / 2),
              (x + w, y + h - eh / 2)],
             [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3,
              Path.CURVE3, Path.CURVE3, Path.LINETO]),
        fill=False, edgecolor=stroke, linewidth=lw(width), zorder=z + 0.2))
    ax.add_patch(Ellipse((x + w / 2, y + eh / 2), w, eh,
                         facecolor=grad[1] if grad else fill, edgecolor=stroke,
                         linewidth=lw(width), zorder=z + 0.3))
    _put_text(ax, x, y + eh / 2, w, h - eh, text, fs, fc, bold, "center", "middle", z + 0.4, 2.0)


def draw_brace(ax, x, y, w, h, color="#2a2a52", width=1.6, z=2.0):
    """竖排大括号，括号尖朝左：把右侧面板与左侧步骤盒连起来（不是箭头）。"""
    mid = y + h / 2
    notch = x + 0.32 * w
    k = 0.05 * h
    verts = [(x + w, y),
             (notch + 0.22 * w, y), (notch, y + 0.13 * h), (notch, mid - k),
             (x, mid),
             (notch, mid + k), (notch, y + 0.87 * h), (notch + 0.22 * w, y + h),
             (x + w, y + h)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    ax.add_patch(PathPatch(Path(verts, codes), fill=False, edgecolor=color,
                           linewidth=lw(width), joinstyle="round", zorder=z))


def _polyline(ax, pts, color, width, ls, z, cap="butt"):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, linewidth=lw(width), linestyle=ls or "solid",
            solid_capstyle=cap, zorder=z, antialiased=True)


def _head(ax, p_from, p_to, size, color, filled, z, width=1.0):
    """在 p_to 处画箭头（实心三角或空心三角）。"""
    dx, dy = p_to[0] - p_from[0], p_to[1] - p_from[1]
    n = hypot(dx, dy)
    if n == 0:
        return
    ux, uy = dx / n, dy / n
    L = max(size, 1.6 * width)
    hw = 0.45 * L
    bx, by = p_to[0] - ux * L, p_to[1] - uy * L
    nx, ny = -uy, ux
    pts = [(bx + nx * hw, by + ny * hw), p_to, (bx - nx * hw, by - ny * hw)]
    if filled:
        ax.add_patch(Polygon(pts, closed=True, facecolor=color, edgecolor=color,
                             linewidth=lw(0.6), joinstyle="miter", zorder=z + 0.1))
    else:
        ax.add_patch(Polygon([pts[0], p_to, pts[2], pts[0]], closed=True, fill=False,
                             edgecolor=color, linewidth=lw(width), joinstyle="miter",
                             zorder=z + 0.1))


def draw_arrow(ax, pts, color=INK, width=1.2, head="block", head_size=5, ls=None,
               head_at_start=False, z=6.0):
    """正交折线连接器。`head` ∈ block(实心) / open(空心) / none(母线、无箭头段)。

    约定：端点离盒边留 1 px，否则视觉上像压在框线上。
    """
    pts = [(float(a), float(b)) for a, b in pts]
    if len(pts) < 2:
        return
    _polyline(ax, pts, color, width, ls, z)
    if head == "none":
        return
    filled = head == "block"
    _head(ax, pts[-2], pts[-1], head_size, color, filled, z, width)
    if head_at_start:
        _head(ax, pts[1], pts[0], head_size, color, filled, z, width)


def draw_curved_arrow(ax, pts, color=INK, width=1.2, head="block", head_size=6, ls=None,
                      head_at_start=False, z=6.0):
    """平滑曲线箭头（循环 / 手绘风弧线）：Catmull-Rom 过所有拐点，末端沿切向加箭头。"""
    pts = [(float(a), float(b)) for a, b in pts]
    if len(pts) < 3:
        return draw_arrow(ax, pts, color, width, head, head_size, ls, head_at_start, z)
    p = np.array([pts[0]] + pts + [pts[-1]], dtype=float)
    out = [p[1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0.0, 1.0, 24)[1:]:
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out = np.array(out)
    ax.plot(out[:, 0], out[:, 1], color=color, linewidth=lw(width), zorder=z,
            linestyle=ls or "solid", solid_capstyle="round")
    if head != "none":
        _head(ax, tuple(out[-6]), tuple(out[-1]), head_size, color, head == "block", z, width)
        if head_at_start:
            _head(ax, tuple(out[5]), tuple(out[0]), head_size, color, head == "block", z, width)


def ortho_points(p_from, p_to, mid_y=None):
    """两点间的正交折线点列：同列直连，异列「先垂到中线、再平、再垂」。"""
    (x0, y0), (x1, y1) = p_from, p_to
    if abs(x0 - x1) < 0.5:
        return [(x0, y0), (x1, y1)]
    my = mid_y if mid_y is not None else (y0 + y1) / 2
    return [(x0, y0), (x0, my), (x1, my), (x1, y1)]


# --------------------------------------------------------------- 指令回放
PRIMITIVES = {
    "box": draw_box, "rect": draw_rect, "text": draw_text, "dashed": draw_dashed_rect,
    "polygon": draw_polygon, "flag": draw_flag, "block_arrow": draw_block_arrow,
    "double_arrow": draw_double_arrow, "diamond": draw_diamond, "hexagon": draw_hexagon,
    "cylinder": draw_cylinder, "brace": draw_brace,
    "arrow": draw_arrow, "curved_arrow": draw_curved_arrow,
}


class Recorder:
    """把绘图指令排队，等画布尺寸定下来后一次性回放（高度自适应的模板需要它）。

    回放顺序 == 入队顺序，与 drawio 里「后面的 cell 压住前面的」画法一致。
    """

    def __init__(self):
        self.ops: list[tuple[str, dict]] = []

    def emit(self, kind, **kw):
        if kind not in PRIMITIVES:
            raise KeyError(f"未知绘图指令: {kind}")
        self.ops.append((kind, kw))

    def paint(self, ax):
        for i, (kind, kw) in enumerate(self.ops):
            args = dict(kw)
            args.setdefault("z", float(2 * i))
            PRIMITIVES[kind](ax, **args)
        return ax

    def canvas(self, w_px, h_px, facecolor="white"):
        pick_cjk_font()
        fig, ax = setup_canvas(w_px, h_px, facecolor)
        self.paint(ax)
        return fig, ax


def add_common_path() -> None:
    """模板脚本在 code/templates/ 下，import common 前调用它把 code/ 加进 sys.path。"""
    code_dir = str(pathlib.Path(__file__).resolve().parent)
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)


def guard(problems, quiet: bool = False) -> None:
    """有超框就逐条报出槽位与预算并非零退出（各模板共用的机器门禁）。"""
    if not problems:
        return
    print(f"✗ 容量检查未通过（{len(problems)} 处超框）：", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    if not quiet:
        print('\n请缩短文案或改用多行（"\\n" 断行），再重新渲染。', file=sys.stderr)
    sys.exit(2)


def output_path(out, content_path) -> pathlib.Path:
    """-o 的后缀一律忽略（`.drawio` 也照常出图），只取文件名；缺省用 content 同名。"""
    if out:
        p = pathlib.Path(out)
        return p.with_suffix("")
    return pathlib.Path(content_path).with_suffix("")
