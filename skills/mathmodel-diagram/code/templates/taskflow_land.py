#!/usr/bin/env python3
"""taskflow-land：横版任务流水线图（若干任务块，块内横向/纵向流水线，块间粗箭头串联）。

    python3 code/templates/taskflow_land.py content.json -o out.png
    python3 code/templates/taskflow_land.py content.json --check

matplotlib 渲染，产出 PNG（300 dpi）+ 同名矢量 PDF。适合"一个课题拆成若干任务、每个任务
是一条处理链、每步下面还要挂做法细节"的场合。横版画布，宽固定 1360，高度按内容自动生长。
段型见 docs/templates/taskflow-land.md。
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import common as C                                            # noqa: E402
from common import DASH, Recorder, lines_of                   # noqa: E402

W = 1360
FS, FS_S, FS_T = 14, 11, 17
INK, WHITE = '#262626', '#ffffff'
# 采样自参考图：深蓝紫步骤盒 + 中紫小盒 + 浅蓝紫面板 + 深蓝强调，全部直角 + 水平渐变
STEP_A, STEP_B = '#2c2c56', '#6f6f9e'           # 步骤盒渐变（深→浅）
STEP2_A, STEP2_B = '#2a5a84', '#5f93bd'         # 蓝色步骤盒渐变
MID_A, MID_B = '#5a549c', '#9a92c4'             # 中紫小盒渐变（白字）
LITE, LITE_S = '#cdd0e8', '#8a86b4'             # 浅紫小盒
LITE2, LITE2_S = '#c6d2ee', '#7f93c4'           # 浅蓝小盒
PANEL, PANEL_S = '#e6e9f8', '#9a96c0'           # 面板底（紫）
PANEL2, PANEL2_S = '#dde5f6', '#7f93c4'         # 面板底（蓝）
BLACK_A = '#0b0b12'                             # 黑底强调盒
ARROW = '#8b8bc0'
FRAME = '#111111'
TITLE_C = '#5a2d6e'
problems: list[str] = []
REC = Recorder()


# ------------------------------------------------------------- 校验与基元
def fit(cid, ls, w, h, fs=FS):
    for ln in ls:
        usable = w - (8 if len(ln) > 1 else 2)
        need = C.text_width(ln, fs)
        if need > usable:
            problems.append(f'{cid}: "{ln}" 宽 {need:.0f}px > 可用 {usable:.0f}px'
                            f'（约 {int(usable // fs)} 个汉字）')
    if len(ls) * (fs + 3) > h:
        problems.append(f'{cid}: {len(ls)} 行需 {len(ls) * (fs + 3)}px，槽高仅 {h:g}px')


def box(cid, x, y, w, h, text, fill, stroke, fs=FS, fc=INK, bold=True, align='center',
        grad=None):
    """直角盒；`grad` 给出渐变终点色时按水平渐变绘制（参考图的主要质感来源）。"""
    ls = lines_of(text)
    fit(cid, ls, w, h, fs)
    REC.emit('box', x=x, y=y, w=w, h=h, text='\n'.join(ls), fill=fill, stroke=stroke,
             width=1.0, fs=fs, fc=fc, bold=bold, radius=0, halign=align,
             grad=(fill, grad) if grad else None)


def label(cid, x, y, w, h, text, fs=FS_T, fc=TITLE_C, align='left'):
    ls = lines_of(text)
    fit(cid, ls, w, h * 1.4, fs)
    REC.emit('text', x=x, y=y, w=w, h=h, text='\n'.join(ls), fs=fs, fc=fc, bold=True,
             halign=align)


def barrow(cid, x, y, w, h, direction='east', fill=ARROW):
    REC.emit('block_arrow', x=x, y=y, w=w, h=h, direction=direction, fill=fill,
             stroke=None, width=1.0, shaft=0.6, head=0.42)


def edge(cid, pts, stroke=INK, width=1.2, head='block'):
    REC.emit('arrow', pts=list(pts), color=stroke, width=width, head=head, head_size=5)


def frame(cid, x, y, w, h):
    REC.emit('dashed', x=x, y=y, w=w, h=h, color=FRAME, width=1.6, ls=DASH)


def dashed_outline(cid, x, y, w, h, color):
    REC.emit('dashed', x=x, y=y, w=w, h=h, color=color, width=1.3, ls=DASH)


# ---------------------------------------------------------------- 段
def rows_of(d):
    """把 detail/side 规范化成行列表。支持字符串、{"items":[…]}、{"rows":[…]}。"""
    if not d:
        return [], None
    if isinstance(d, str):
        return [{'full': d}], None
    if 'rows' in d:
        return d['rows'], d.get('frame')
    if 'items' in d:
        return [{'full': i} for i in d['items']], d.get('frame', 'blue')
    return [], None


def row_h(r):
    if 'cols' in r:
        return 26
    if 'table' in r:
        return len(r['table']) * 28
    return max(24, len(lines_of(r.get('full', ''))) * 15 + 9)


def detail_h(d):
    rs, fr = rows_of(d)
    if not rs:
        return 0
    return sum(row_h(r) + 6 for r in rs) + (10 if fr else 2)


def sec_h(s):
    t = s['type']
    if t == 'pipeline':
        return 34 + (max(detail_h(st.get('detail')) for st in s['steps']) or 0) + 6
    if t == 'vchain':
        return sum(max(38, detail_h(st.get('side'))) + 14 for st in s['steps'])
    if t == 'pairs':
        lh = len(s['left']) * 46
        rh = sum(max(38, len(lines_of(i)) * 18 + 10) + 10 for i in s['right'])
        return max(lh, rh)
    sys.exit(f'未知段型 {t}')


def draw_detail(cid, d, x, y, w, tone2=False):
    """详情面板：若干行，每行可为并排小盒 / 通栏说明 / 两列表格；可加虚线外框。"""
    rs, fr = rows_of(d)
    if not rs:
        return 0
    L, LS = (LITE2, LITE2_S) if tone2 else (LITE, LITE_S)
    P, PS = (PANEL2, PANEL2_S) if tone2 else (PANEL, PANEL_S)
    h = detail_h(d)
    REC.emit('rect', x=x, y=y, w=w, h=h, fill=P)
    if fr:
        dashed_outline(f'{cid}_ol', x, y, w, h, FRAME if fr == 'black' else PS)
    iy = y + (6 if fr else 2)
    ix, iw = x + 6, w - 12
    for j, r in enumerate(rs):
        hh = row_h(r)
        if 'cols' in r:                       # 并排深色小盒，白字
            for i, (cx, cw) in enumerate(C.slots(ix, ix + iw, len(r['cols']), 8)):
                box(f'{cid}_r{j}c{i}', cx, iy, cw, hh, r['cols'][i], MID_A, MID_A,
                    FS_S, fc=WHITE, grad=MID_B)
        elif 'table' in r:                    # 左名称 / 右内容，中间短横线
            for i, (lt, rt) in enumerate(r['table']):
                ry = iy + i * 28
                box(f'{cid}_r{j}t{i}l', ix, ry, iw * 0.52, 24, lt, L, LS, FS_S)
                box(f'{cid}_r{j}t{i}r', ix + iw * 0.58, ry, iw * 0.42, 24, rt, L, LS, FS_S)
                edge(f'{cid}_r{j}t{i}e', [(ix + iw * 0.53, ry + 12),
                                          (ix + iw * 0.575, ry + 12)], LS, 1.2, 'none')
        else:                                 # 通栏说明
            box(f'{cid}_r{j}f', ix, iy, iw, hh, r['full'], L, LS, FS_S, bold=False)
        iy += hh + 6
    return h


def step_style(st):
    if st.get('emph') == 'black':
        return BLACK_A, BLACK_A, WHITE, None
    if st.get('emph'):
        return STEP2_A, STEP2_A, WHITE, STEP2_B
    return STEP_A, STEP_A, WHITE, STEP_B


def draw_sec(k, s, x0, x1, y):
    t, h = s['type'], sec_h(s)

    if t == 'pipeline':
        steps, gap = s['steps'], 32
        for i, (sx, sw) in enumerate(C.slots(x0 + 10, x1 - 10, len(steps), gap)):
            st = steps[i]
            f1, f2, fc, gr = step_style(st)
            box(f'{k}_s{i}', sx, y, sw, 30, st['text'], f1, f2, FS, fc=fc, grad=gr)
            if st.get('detail'):
                draw_detail(f'{k}_d{i}', st['detail'], sx, y + 36, sw, st.get('tone2', False))
            if i:
                barrow(f'{k}_a{i}', sx - gap + 4, y + 6, gap - 8, 18)
        return h

    if t == 'vchain':
        yy, lw = y, (x1 - x0) * 0.28
        for i, st in enumerate(s['steps']):
            hh = max(38, detail_h(st.get('side')))
            f1, f2, fc, gr = step_style(st)
            box(f'{k}_v{i}', x0 + 8, yy + (hh - 34) / 2, lw, 34, st['text'], f1, f2,
                FS, fc=fc, grad=gr)
            if st.get('side'):
                px = x0 + 8 + lw + 26
                draw_detail(f'{k}_vs{i}', st['side'], px, yy, x1 - 12 - px,
                            st.get('tone2', False))
                REC.emit('brace', x=x0 + 8 + lw + 6, y=yy + 4, w=14, h=hh - 8,
                         color='#2a2a52', width=1.6)
            if i:
                barrow(f'{k}_va{i}', x0 + 8 + lw / 2 - 8, yy - 13, 16, 12, 'south')
            yy += hh + 14
        return h

    if t == 'pairs':
        L, R = s['left'], s['right']
        lw = (x1 - x0) * 0.36
        lx, rx = x0 + 10, x0 + 10 + (x1 - x0) * 0.46
        rw = x1 - 10 - rx
        for i, it in enumerate(L):
            box(f'{k}_pl{i}', lx, y + i * 46, lw, 36, it, MID_A, MID_A, FS,
                fc=WHITE, grad=MID_B)
        ry = y
        for i, it in enumerate(R):
            ih = max(38, len(lines_of(it)) * 18 + 10)
            box(f'{k}_pr{i}', rx, ry, rw, ih, it, PANEL, PANEL_S, FS_S, align='left')
            barrow(f'{k}_pa{i}', lx + lw + 8, ry + ih / 2 - 9, (rx - lx - lw) - 16, 18)
            ry += ih + 10
        return h

    sys.exit(f'未知段型 {t}')


# ---------------------------------------------------------------- 主体
def build(c):
    blocks = c['blocks']
    PAD, GAP, TOP = 22, 34, 40
    rows, i = [], 0
    while i < len(blocks):
        if blocks[i].get('layout') == 'half' and i + 1 < len(blocks) \
                and blocks[i + 1].get('layout') == 'half':
            rows.append([blocks[i], blocks[i + 1]])
            i += 2
        else:
            rows.append([blocks[i]])
            i += 1

    y = TOP
    for ri, row in enumerate(rows):
        spans = C.slots(60, W - 60, len(row), 56) if len(row) > 1 else [(60, W - 120)]
        rh = 0
        for bi, b in enumerate(row):
            bx, bw = spans[bi]
            secs = [sec_h(s) for s in b['sections']]
            bh = PAD + sum(secs) + (len(secs) - 1) * 14 + PAD
            rh = max(rh, bh)
            label(f'r{ri}b{bi}_t', bx + 4, y - 26, bw - 8, 24, b['title'])
            if b.get('cylinder') and bi + 1 < len(row):   # 两个半宽块之间的圆柱中转标签
                gx = bx + bw
                gw = spans[bi + 1][0] - gx
                cw2 = min(58, gw - 20)
                cx2 = gx + (gw - cw2) / 2
                cy2 = y + 40
                REC.emit('cylinder', x=cx2, y=cy2, w=cw2, h=118,
                         text=C.stack(b['cylinder']), fill=PANEL, stroke=PANEL_S,
                         width=1.2, fs=FS_T, fc=TITLE_C, bold=True,
                         grad=(PANEL, '#ffffff'))
                barrow(f'r{ri}b{bi}_cyla', cx2 + cw2 + 4, cy2 + 46, gw / 2 - 10, 26)
            frame(f'r{ri}b{bi}', bx, y, bw, bh)
            yy = y + PAD
            for si, s in enumerate(b['sections']):
                yy += draw_sec(f'r{ri}b{bi}s{si}', s, bx, bx + bw, yy) + 14
        if ri + 1 < len(rows):
            barrow(f'flow{ri}', W / 2 - 18, y + rh + 4, 36, GAP - 12, 'south')
        y += rh + GAP
    return int(y + 10)


def main():
    ap = argparse.ArgumentParser(
        description='渲染横版任务流水线图（matplotlib：PNG 300dpi + 矢量 PDF）')
    ap.add_argument('content')
    ap.add_argument('-o', '--out')
    ap.add_argument('--check', action='store_true', help='只跑容量校验')
    a = ap.parse_args()
    c = json.loads(pathlib.Path(a.content).read_text(encoding='utf-8'))
    H = build(c)
    C.guard(problems)
    print(f'✓ 容量检查通过（画布 {W}×{H}）')
    if a.check:
        return
    fig, _ = REC.canvas(W, H)
    png, pdf = C.save_figure(fig, C.output_path(a.out, a.content))
    print(f'✓ 已写出 {png}（300 dpi）与 {pdf}（矢量），共 {len(REC.ops)} 个图元')


if __name__ == '__main__':
    main()
