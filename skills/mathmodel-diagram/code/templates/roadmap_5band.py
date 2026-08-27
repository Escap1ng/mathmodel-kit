#!/usr/bin/env python3
"""roadmap-5band：五带技术路线图（matplotlib 渲染 → PNG 300dpi + 矢量 PDF）。

    python3 code/templates/roadmap_5band.py content.json -o out.png
    python3 code/templates/roadmap_5band.py content.json --check   # 只校验容量

几何是照参考图逐像素标定的固定 954×1296 模板，只有各族内部的数量可变（2–5，
按族而定）。坐标系 1 px = 0.01 inch、y 轴向下（见 code/common.py），所以这些
常量与标定时的像素值完全一致。写图之前逐槽做中文字宽校验：CJK/全角 = 字号 px、
半角 = 字号/2、行高 = 字号 + 3，超框报出具体槽位与预算并非零退出。
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import common as C                                            # noqa: E402
from common import DASH, DOT, Recorder                        # noqa: E402

# ----------------------------------------------------------------- style
PAGE, FRAME = '#f2eef7', '#808080'
TITLE_F, BAND_S, BLOCK = '#4f80bd', '#5b6b78', '#4874cc'
TXT = '#262626'
FS = 16                      # single flat font size, as in the reference
LINE_H = 19          # 16 px 字号的实测行高 = 字号 + 3

PALETTE = {                  # per band: (box fill, box stroke, accent fill, chevron fill)
    1: ('#eef6fd', '#3b547f', '#b6d8f6', '#98d0ed'),
    2: ('#eef6fd', '#3b547f', '#b6d8f6', '#a2d2ea'),
    3: ('#fcead9', '#c08b5c', '#fddecd', '#f8d5b3'),
    4: ('#e5dfeb', '#9b979f', '#ccc2db', '#c8c1d9'),
    5: ('#dbeef4', '#668d89', '#bae2e4', '#d4eae4'),
}
EDGE = {1: '#1f3f6b', 2: '#1f3f6b', 3: '#7b5530', 4: '#7f5faf', 5: '#5f8484'}
TEAL_S = '#4f8f8b'

# ------------------------------------------------------------- geometry
CANVAS_W, CANVAS_H = 954, 1296
BAND_X, BAND_W = 124, 719
BANDS = {1: (75, 126), 2: (219, 294), 3: (530, 252), 4: (799, 204), 5: (1021, 234)}
CHEV_Y = {1: 94, 2: 322, 3: 599, 4: 855, 5: 1103}
RAIL_CY = {1: 138, 2: 366, 3: 656, 4: 901, 5: 1138}
FLOW_Y = [203, 514, 782, 1005]

problems: list[str] = []
REC = Recorder()


# ------------------------------------------------------------- helpers
def fit(slot, lines, w, h, vertical=False):
    """Record a capacity problem if the text cannot fit the slot."""
    if vertical:
        need_h = len(lines) * LINE_H
        if need_h > h:
            problems.append(f'{slot}: 竖排 {len(lines)} 字需 {need_h}px，槽高仅 {h:g}px'
                            f'（最多 {int(h // LINE_H)} 字）')
        return
    usable = w - 8
    for ln in lines:
        need = C.text_width(ln, FS)
        if need > usable:
            problems.append(f'{slot}: "{ln}" 宽 {need:.0f}px > 可用 {usable:.0f}px'
                            f'（约 {int(usable // FS)} 个汉字）')
    if len(lines) * LINE_H > h:
        problems.append(f'{slot}: {len(lines)} 行需 {len(lines) * LINE_H}px，槽高仅 {h:g}px'
                        f'（最多 {int(h // LINE_H)} 行）')


def arrow(pts, stroke, width=1.2, head='block', head_size=5, ls=None, curved=False,
          head_at_start=False):
    """正交折线连接器；`head='none'` 画母线/无箭头段，`curved` 画平滑弧。"""
    kind = 'curved_arrow' if curved else 'arrow'
    REC.emit(kind, pts=list(pts), color=stroke, width=width, head=head,
             head_size=head_size, ls=ls, head_at_start=head_at_start)


def dashrect(x, y, w, h, color, ls=DASH, width=1.0):
    """虚线/点线矩形框（分带用 DOT，分组框用 DASH）。"""
    REC.emit('dashed', x=x, y=y, w=w, h=h, color=color, ls=ls, width=width)


def box_style(fill, stroke):
    return dict(fill=fill, stroke=stroke, width=1.0, fs=FS, fc=TXT, bold=True)


def tbox(cid, x, y, w, h, fill, stroke, value, arc=8):
    ls = C.lines_of(value)
    fit(cid, ls, w, h)
    REC.emit('box', x=x, y=y, w=w, h=h, text='\n'.join(ls), radius=C.radius_of(w, h, arc),
             **box_style(fill, stroke))


def vbox(cid, x, y, w, h, fill, stroke, value, arc=8):
    if w < FS + 6:
        problems.append(f'{cid}: 竖排槽宽 {w:g}px 不足（需 ≥ {FS + 6}px），请减少该组数量')
    chars = list(str(value))
    fit(cid, chars, w, h, vertical=True)
    REC.emit('box', x=x, y=y, w=w, h=h, text=C.stack(value),
             radius=C.radius_of(w, h, arc), **box_style(fill, stroke))


def tlabel(cid, x, y, w, h, value, fc=TXT):
    # 透明标签没有边框，纵向溢出无害；宽度仍然严格，因为左右都贴着邻居
    ls = C.lines_of(value)
    fit(cid, ls, w, h * 1.4)
    REC.emit('text', x=x, y=y, w=w, h=h, text='\n'.join(ls), fs=FS, fc=fc, bold=True)


def need(d, key, ctx):
    if key not in d:
        sys.exit(f'content 缺少字段: {ctx}.{key}')
    return d[key]


# ------------------------------------------------------------- bands
def build(c):
    # ---- page furniture -------------------------------------------------
    REC.emit('rect', x=0, y=0, w=46, h=CANVAS_H, fill=PAGE)
    REC.emit('rect', x=46, y=0, w=CANVAS_W - 46, h=28, fill=PAGE)

    title = C.lines_of(need(c, 'title', 'root'))
    fit('title', title, 719, 38)
    REC.emit('box', x=124, y=31, w=719, h=38, text='\n'.join(title), fill=TITLE_F,
             stroke=TITLE_F, width=1.0, fs=FS, fc='#ffffff', bold=True, radius=0)

    for b, (by, bh) in BANDS.items():
        dashrect(BAND_X, by, BAND_W, bh, BAND_S, DOT)

    rails = need(c, 'rails', 'root')
    if len(rails) != 5:
        sys.exit('rails 必须正好 5 项（每带一项）')
    lab_gaps = []
    for i, r in enumerate(rails, 1):
        cv = str(r['chevron'])
        fit(f'chev{i}', list(cv), 60, 92, vertical=True)
        REC.emit('flag', x=58, y=CHEV_Y[i], w=60, h=92, text=C.stack(cv),
                 fill=PALETTE[i][3], stroke='#5b93bd', width=1.0, tip=0.22,
                 fs=FS, fc=TXT, bold=True, text_dx=-10)
        txt = str(r['label'])
        h = len(txt) * 23
        y = RAIL_CY[i] - h // 2
        fit(f'rail{i}', list(txt), 26, h, vertical=True)
        REC.emit('text', x=860, y=y, w=26, h=h, text=C.stack(txt), fs=FS,
                 fc='#3b547f', bold=True)
        lab_gaps.append((y - 2, y + h + 2))

    # outer loop frame, interrupted where the title / chevrons / rails cover it
    arrow([(68, 49), (123, 49)], FRAME, 1, 'none')
    arrow([(844, 49), (874, 49)], FRAME, 1, 'none')
    arrow([(68, 1273), (874, 1273)], FRAME, 1, 'none')

    def segs(y0, y1, gaps):
        out, cur = [], y0
        for g0, g1 in gaps:
            if g0 > cur:
                out.append((cur, g0))
            cur = max(cur, g1)
        if cur < y1:
            out.append((cur, y1))
        return out

    for ya, yb in segs(49, 1273, [(y - 1, y + 93) for y in CHEV_Y.values()]):
        arrow([(68, ya), (68, yb)], FRAME, 1, 'none')
    for ya, yb in segs(49, 1273, lab_gaps):
        arrow([(874, ya), (874, yb)], FRAME, 1, 'none')
    for ay in FLOW_Y:
        REC.emit('block_arrow', x=470, y=ay, w=30, h=17, direction='south',
                 fill=BLOCK, stroke=BLOCK, width=1.0, shaft=0.62, head=0.5)

    band1(c.get('band1', {}))
    band2(c.get('band2', {}))
    band3(c.get('band3', {}))
    band4(c.get('band4', {}))
    band5(c.get('band5', {}))


def band1(d):
    f, s, acc, _ = PALETTE[1]
    tbox('b1_head', 326, 87, 309, 34, acc, s, need(d, 'headline', 'band1'), arc=0)
    items = need(d, 'items', 'band1')
    if not 2 <= len(items) <= 4:
        sys.exit('band1.items 需 2–4 项')
    for i, (x, w) in enumerate(C.slots(185, 779, len(items), 43), 1):
        tbox(f'b1_{i}', x, 157, w, 33, f, s, items[i - 1], arc=0)
    centers = [x + w / 2 for x, w in C.slots(185, 779, len(items), 43)]
    arrow([(480, 122), (480, 138)], EDGE[1], head='none')
    arrow([(centers[0], 138), (centers[-1], 138)], EDGE[1], head='none')
    for cx in centers:
        arrow([(cx, 138), (cx, 156)], EDGE[1])


def band2(d):
    f, s, acc, _ = PALETTE[2]
    e = EDGE[2]
    src = need(d, 'sources', 'band2')
    if not 2 <= len(src) <= 4:
        sys.exit('band2.sources 需 2–4 项')
    sl = C.slots(136, 381, len(src), 11)
    for i, (x, w) in enumerate(sl, 1):
        tbox(f'b2_src{i}', x, 238, w, 48, f, s, src[i - 1])
    cx_all = [x + w / 2 for x, w in sl]
    mid = (136 + 381) / 2
    for cx in cx_all:
        if abs(cx - mid) > 1:
            arrow([(cx, 287), (cx, 305)], e, head='none')
    arrow([(cx_all[0], 305), (cx_all[-1], 305)], e, head='none')
    arrow([(mid, 305), (mid, 317)], e)

    tbox('b2_prep', 211, 318, 95, 34, f, s, need(d, 'prep', 'band2'))
    tbox('b2_assume', 192, 383, 133, 64, f, s, need(d, 'assumptions', 'band2'))
    tbox('b2_symbol', 192, 471, 133, 33, f, s, need(d, 'symbols', 'band2'))
    arrow([(258, 353), (258, 382)], e)
    arrow([(258, 448), (258, 470)], e)

    vbox('b2_lv', 367, 396, 43, 104, acc, s, need(d, 'left_vertical', 'band2'))
    arrow([(326, 415), (366, 415)], e)
    tbox('b2_c1', 401, 245, 155, 89, acc, s, need(d, 'content', 'band2'), arc=0)
    arrow([(478, 335), (478, 354)], e)

    BLUE = '#3b6fbf'
    # 子框左侧要让位给标题，所以四条边各拆成两段（小虚线框画成闭合折线即可）
    arrow([(417, 355), (539, 355)], BLUE, 1, 'none', ls=DASH)
    arrow([(417, 503), (539, 503)], BLUE, 1, 'none', ls=DASH)
    arrow([(417, 355), (417, 436)], BLUE, 1, 'none', ls=DASH)
    arrow([(417, 460), (417, 503)], BLUE, 1, 'none', ls=DASH)
    arrow([(539, 355), (539, 436)], BLUE, 1, 'none', ls=DASH)
    arrow([(539, 460), (539, 503)], BLUE, 1, 'none', ls=DASH)
    tlabel('b2_subtitle', 421, 358, 114, 24, need(d, 'subframe', 'band2'))
    dims = need(d, 'dims', 'band2')
    if not 2 <= len(dims) <= 4:
        sys.exit('band2.dims 需 2–4 项')
    for i, (y, h) in enumerate(C.slots(391, 494, len(dims), 10), 1):
        tbox(f'b2_dim{i}', 433, y, 93, h, '#ffffff', s, dims[i - 1], arc=0)

    vbox('b2_rv', 548, 398, 43, 102, acc, s, need(d, 'right_vertical', 'band2'))
    arrow([(411, 448), (430, 448)], s, 2, 'open', 14)
    arrow([(547, 448), (528, 448)], s, 2, 'open', 14)

    dashrect(591, 235, 245, 155, BLUE)
    met = need(d, 'metrics', 'band2')
    if not 2 <= len(met) <= 4:
        sys.exit('band2.metrics 需 2–4 行')
    for i, (y, h) in enumerate(C.slots(248, 380, len(met), 8), 1):
        tbox(f'b2_ml{i}', 603, y, 64, h, f, s, met[i - 1][0], arc=0)
        tbox(f'b2_mr{i}', 677, y, 147, h, f, s, met[i - 1][1], arc=0)

    tbox('b2_agg', 650, 410, 126, 31, f, s, need(d, 'aggregator', 'band2'), arc=0)
    tbox('b2_data', 604, 460, 220, 44, f, s, need(d, 'datasource', 'band2'), arc=0)
    arrow([(713, 390), (713, 409)], e)
    arrow([(690, 459), (690, 442)], e)
    arrow([(649, 425), (592, 425)], e)


def band3(d):
    f, s, acc, _ = PALETTE[3]
    e = EDGE[3]
    tbox('b3_top', 415, 542, 136, 35, f, s, need(d, 'top', 'band3'), arc=50)
    tbox('b3_bot', 414, 738, 136, 35, f, s, need(d, 'bottom', 'band3'), arc=50)
    left, right = need(d, 'left', 'band3'), need(d, 'right', 'band3')
    if not 2 <= len(left) <= 4 or not 2 <= len(right) <= 4:
        sys.exit('band3.left / band3.right 需各 2–4 项')
    rows_l = C.slots(600, 714, len(left), 12)
    rows_r = C.slots(600, 714, len(right), 12)
    for i, (y, h) in enumerate(rows_l, 1):
        tbox(f'b3_l{i}', 140, y, 144, h, f, s, left[i - 1])
    for i, (y, h) in enumerate(rows_r, 1):
        tbox(f'b3_r{i}', 677, y, 155, h, f, s, right[i - 1])
    vbox('b3_lv', 314, 587, 44, 140, f, s, need(d, 'left_vertical', 'band3'))
    vbox('b3_rv', 608, 587, 44, 140, f, s, need(d, 'right_vertical', 'band3'))
    tbox('b3_c2', 382, 604, 203, 105, acc, s, need(d, 'content', 'band3'), arc=0)

    def bracket(rows, x_box_edge, x_spine, x_target):
        """多盒 → 竖母线 → 一根箭头进中心（一分多/多合一的画法）。"""
        cys = [y + h / 2 for y, h in rows]
        for cy in cys:
            arrow([(x_box_edge, cy), (x_spine, cy)], e, head='none')
        arrow([(x_spine, cys[0]), (x_spine, cys[-1])], e, head='none')
        arrow([(x_spine, 657), (x_target, 657)], e)

    bracket(rows_l, 285, 296, 313)
    bracket(rows_r, 676, 665, 653)
    arrow([(359, 657), (381, 657)], e)
    arrow([(607, 657), (586, 657)], e)
    arrow([(414, 559), (336, 559), (336, 586)], e)
    arrow([(552, 559), (630, 559), (630, 586)], e)
    arrow([(336, 728), (336, 755), (413, 755)], e)
    arrow([(630, 728), (630, 755), (551, 755)], e)


def band4(d):
    f, s, acc, _ = PALETTE[4]
    tf, ts, tacc = PALETTE[5][0], PALETTE[5][1], PALETTE[5][2]
    tbox('b4_banner', 136, 808, 697, 29, acc, '#8d84a8', need(d, 'banner', 'band4'), arc=0)
    dashrect(134, 846, 307, 145, '#7f5faf')
    dashrect(527, 846, 307, 145, '#7f5faf')

    vbox('b4_lv', 153, 855, 41, 126, acc, '#8d84a8', need(d, 'left_vertical', 'band4'))
    li = need(d, 'left_items', 'band4')
    if not 3 <= len(li) <= 5:
        sys.exit('band4.left_items 需 3–5 项')
    for i, (y, h) in enumerate(C.slots(856, 981, len(li), 3), 1):
        tbox(f'b4_s{i}', 275, y, 147, h, f, s, li[i - 1], arc=0)
    la = d.get('left_arrow_labels', ['', ''])
    arrow([(196, 905), (272, 905)], EDGE[4])
    tlabel('b4_la1', 196, 878, 76, 22, la[0])
    tlabel('b4_la2', 196, 910, 76, 22, la[1] if len(la) > 1 else '')

    tlabel('b4_mid', 448, 845, 95, 55, need(d, 'middle', 'band4'))
    REC.emit('double_arrow', x=442, y=894, w=82, h=23, fill='#d9d9d9',
             stroke='#9a9a9a', width=1.0, shaft=0.4, head=0.28)

    vbox('b4_rv', 547, 857, 36, 121, tacc, TEAL_S, need(d, 'right_vertical', 'band4'))
    ri = need(d, 'right_items', 'band4')
    if not 3 <= len(ri) <= 5:
        sys.exit('band4.right_items 需 3–5 项')
    for i, (y, h) in enumerate(C.slots(857, 978, len(ri), 3), 1):
        tbox(f'b4_v{i}', 650, y, 89, h, tf, ts, ri[i - 1], arc=0)
    ra = d.get('right_arrow_labels', ['', ''])
    arrow([(584, 905), (648, 905)], TEAL_S)
    tlabel('b4_ra1', 584, 878, 64, 22, ra[0])
    tlabel('b4_ra2', 584, 910, 64, 22, ra[1] if len(ra) > 1 else '')

    spans = need(d, 'right_spans', 'band4')
    if not 1 <= len(spans) <= 3:
        sys.exit('band4.right_spans 需 1–3 项')
    for i, (y, h) in enumerate(C.slots(857, 979, len(spans), 3), 1):
        tbox(f'b4_o{i}', 742, y, 76, h, tf, ts, spans[i - 1], arc=0)


def band5(d):
    f, s, acc, _ = PALETTE[5]
    e = EDGE[5]
    pu, pus, puacc = PALETTE[4][0], PALETTE[4][1], PALETTE[4][2]
    li = need(d, 'left_items', 'band5')
    if not 3 <= len(li) <= 5:
        sys.exit('band5.left_items 需 3–5 项')
    for i, (y, h) in enumerate(C.slots(1030, 1188, len(li), 9), 1):
        tbox(f'b5_p{i}', 140, y, 100, h, pu, pus, li[i - 1])
    tbox('b5_corner', 138, 1199, 104, 53, puacc, '#8d84a8', need(d, 'corner', 'band5'), arc=25)
    tbox('b5_pill', 262, 1215, 184, 37, puacc, '#8d84a8', need(d, 'pill', 'band5'), arc=50)

    dashrect(259, 1030, 190, 158, '#4f8fbf', DOT)
    cyc = need(d, 'cycle', 'band5')
    if len(cyc) != 3:
        sys.exit('band5.cycle 必须正好 3 项（三元循环）')
    tlabel('b5_cy1', 272, 1080, 72, 22, cyc[0])
    tlabel('b5_cy2', 370, 1080, 72, 22, cyc[1])
    tlabel('b5_cy3', 326, 1158, 72, 22, cyc[2])
    CY = dict(width=9, head='block', head_size=2, curved=True)
    arrow([(330, 1068), (348, 1040), (386, 1050)], '#ccccd6', **CY)
    arrow([(276, 1106), (288, 1142), (326, 1152)], '#ccccd6', **CY)
    arrow([(392, 1152), (432, 1140), (436, 1104)], '#ccccd6', **CY)
    arrow([(354, 1214), (354, 1190)], EDGE[4])

    tbox('b5_c4', 462, 1039, 139, 107, acc, TEAL_S, need(d, 'content', 'band5'), arc=0)
    hexl = C.lines_of(need(d, 'hex', 'band5'))
    fit('b5_hex', hexl, 57, 59)
    REC.emit('hexagon', x=623, y=1061, w=57, h=59, text='\n'.join(hexl), fill=acc,
             stroke=TEAL_S, width=1.0, size=12, fs=FS, fc=TXT, bold=True)
    tbox('b5_eval', 716, 1031, 86, 31, f, s, need(d, 'eval', 'band5'), arc=0)
    arrow([(715, 1046), (651, 1046), (651, 1060)], e)
    arrow([(622, 1090), (602, 1090)], e)

    met = need(d, 'metrics', 'band5')
    if not 2 <= len(met) <= 5:
        sys.exit('band5.metrics 需 2–5 项')
    cols = C.slots(689, 829, len(met), 7)
    for i, (x, w) in enumerate(cols, 1):
        vbox(f'b5_m{i}', x, 1109, w, 124, f, s, met[i - 1])
    arrow([(759, 1063), (759, 1085)], e, head='none')
    arrow([(cols[0][0] + cols[0][1] / 2, 1085), (cols[-1][0] + cols[-1][1] / 2, 1085)],
          e, head='none')
    for x, w in cols:
        arrow([(x + w / 2, 1085), (x + w / 2, 1108)], e)

    cases = need(d, 'cases', 'band5')
    if not 1 <= len(cases) <= 3:
        sys.exit('band5.cases 需 1–3 项')
    # the case frame is bottom-anchored at y=1242 and grows upward with the item count,
    # so 3 items still get a legible 23px row instead of being squeezed into 14px
    bh, gp = (26, 8) if len(cases) <= 2 else (23, 6)
    inner = len(cases) * bh + (len(cases) - 1) * gp
    top = 1233 - inner
    REC.emit('rect', x=560, y=top - 4, w=109, h=inner + 8, fill='#fdf7ec')
    dashrect(559, top - 5, 111, inner + 10, '#d09a50')
    for i in range(len(cases)):
        tbox(f'b5_case{i + 1}', 567, top + i * (bh + gp), 96, bh,
             PALETTE[3][0], PALETTE[3][1], cases[i], arc=30)
    arrow([(556, 1205), (556, 1147)], e)


# ------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(
        description='渲染五带技术路线图（matplotlib：PNG 300dpi + 矢量 PDF）')
    ap.add_argument('content', help='content JSON path')
    ap.add_argument('-o', '--out', default=None, help='output path（后缀忽略，一律出 png+pdf）')
    ap.add_argument('--check', action='store_true', help='only run the capacity check')
    a = ap.parse_args()

    c = json.loads(pathlib.Path(a.content).read_text(encoding='utf-8'))
    build(c)
    C.guard(problems)
    print(f'✓ 容量检查通过（画布 {CANVAS_W}×{CANVAS_H}）')
    if a.check:
        return
    fig, _ = REC.canvas(CANVAS_W, CANVAS_H)
    png, pdf = C.save_figure(fig, C.output_path(a.out, a.content))
    print(f'✓ 已写出 {png}（300 dpi）与 {pdf}（矢量），共 {len(REC.ops)} 个图元')


if __name__ == '__main__':
    main()
