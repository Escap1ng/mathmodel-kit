#!/usr/bin/env python3
"""stageflow-3col：分阶段流程框架图（左方法链 / 中彩色流程块 / 右阶段说明）。

    python3 code/templates/stageflow_3col.py content.json -o out.png
    python3 code/templates/stageflow_3col.py content.json --check

matplotlib 渲染，产出 PNG（300 dpi）+ 同名矢量 PDF。与 framework-3col 的区别：中栏每块有
**实色标题条**和独立色系，左右栏是**竖排文字**（左＝白底方框 + 粗箭头推进，右＝左向块箭头
指入对应块）。段型见 docs/templates/stageflow-3col.md。
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import common as C                                            # noqa: E402
from common import DASH, Recorder, lines_of                   # noqa: E402

W = 1000
FS, FS_T = 14, 16
INK = '#262626'
PINK, PINK_S = '#fbe4ec', '#d2679f'
RAIL_S, RAIL_ARROW = '#1f3f7f', '#1f3f7f'
RRAIL, RRAIL_S = '#a8c0ea', '#4060b0'
MID = (150, 800)                      # 中栏容器 x 范围
RAIL_L = (58, 130)                    # 左栏竖排盒
RAIL_R = (820, 960)                   # 右栏箭头

# 每块一个色系：(标题条底, 标题条描边, 深内容, 浅内容, 描边)
TONES = {
    'teal':   ('#1f6f6f', '#14504f', '#a8e0e0', '#d6f2f2', '#4a9a9a'),
    'green':  ('#3a5a22', '#2a4318', '#c8e8b0', '#e6f4dc', '#6a9a4a'),
    'olive':  ('#8a7a1a', '#665a12', '#f6e6a4', '#fbf3d2', '#b8a23a'),
    'orange': ('#d06818', '#a04e10', '#f8d0b0', '#fbe6d6', '#d98c50'),
    'blue':   ('#4060b0', '#2c4488', '#a8c0ea', '#cfdcf4', '#5f7fc8'),
}
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


def box(cid, x, y, w, h, text, fill, stroke, fs=FS, fc=INK, arc=12, bold=True):
    ls = lines_of(text)
    fit(cid, ls, w, h, fs)
    REC.emit('box', x=x, y=y, w=w, h=h, text='\n'.join(ls), fill=fill, stroke=stroke,
             width=1.4, fs=fs, fc=fc, bold=bold, radius=C.radius_of(w, h, arc))


def vbox(cid, x, y, w, h, text, fill, stroke, fs=FS_T, fc=INK, arc=12):
    chars = list(str(text))
    if len(chars) * (fs + 3) > h:
        problems.append(f'{cid}: 竖排 {len(chars)} 字需 {len(chars) * (fs + 3)}px > 槽高 {h:g}px')
    REC.emit('box', x=x, y=y, w=w, h=h, text=C.stack(text), fill=fill, stroke=stroke,
             width=2.0, fs=fs, fc=fc, bold=True, radius=C.radius_of(w, h, arc))


def diamond(cid, x, y, w, h, text, fill, stroke, fs=FS):
    ls = lines_of(text)
    REC.emit('diamond', x=x, y=y, w=w, h=h, text='\n'.join(ls), fill=fill, stroke=stroke,
             width=1.4, fs=fs, fc=INK, bold=True)


def edge(cid, pts, stroke=INK, width=1.6, head='block', head_at_start=False, ls=None):
    REC.emit('arrow', pts=list(pts), color=stroke, width=width, head=head, head_size=6,
             ls=ls, head_at_start=head_at_start)


def dashframe(cid, x, y, w, h, color='#5a5a5a'):
    REC.emit('dashed', x=x, y=y, w=w, h=h, color=color, width=1.2, ls=DASH)


def barrow(cid, x, y, w, h, direction, fill, stroke=None, shaft=0.5, head=0.32,
           text=None, fs=FS_T, fc=INK, width=1.0):
    REC.emit('block_arrow', x=x, y=y, w=w, h=h, direction=direction, fill=fill,
             stroke=stroke, width=width, shaft=shaft, head=head, text=text, fs=fs,
             fc=fc, bold=True)


# ---------------------------------------------------------------- 段
def sec_h(s):
    t = s['type']
    if t == 'cards':
        return 40 + max(len(lines_of(c['desc'])) for c in s['cards']) * 18 + 22
    if t == 'groups':
        return 34 + max(len(g['items']) for g in s['groups']) * 32
    if t == 'list_grid':
        return 34 + max(len(s['left']['items']), len(s['right']['rows'])) * 32
    if t == 'scenarios':
        return 40 + 120 + 44
    if t == 'fanout':
        return 40 + 12 + 46
    sys.exit(f'未知段型 {t}')


def draw_sec(k, s, x0, x1, y, tone):
    TB, TBS, DEEP, LIGHT, STK = TONES[tone]
    t, h = s['type'], sec_h(s)

    if t == 'cards':
        cs = s['cards']
        dh = max(len(lines_of(c['desc'])) for c in cs) * 18 + 12
        for i, (cx, cw) in enumerate(C.slots(x0 + 14, x1 - 14, len(cs), 10)):
            box(f'{k}_ch{i}', cx, y, cw, 30, cs[i]['header'], DEEP, STK)
            box(f'{k}_cd{i}', cx, y + 36, cw, dh, cs[i]['desc'], LIGHT, STK, fs=12,
                bold=False)
        return h

    if t == 'groups':
        gs = s['groups']
        for i, (gx, gw) in enumerate(C.slots(x0 + 14, x1 - 14, len(gs), 34)):
            dashframe(f'{k}_gf{i}', gx - 8, y - 6, gw + 16, h - 4)
            box(f'{k}_gh{i}', gx, y, gw, 28, gs[i]['header'], DEEP, STK)
            for j, it in enumerate(gs[i]['items']):
                box(f'{k}_gi{i}_{j}', gx, y + 34 + j * 32, gw, 27, it, LIGHT, STK)
            if i:
                edge(f'{k}_ga{i}', [(gx - 30, y + h / 2 - 10), (gx - 10, y + h / 2 - 10)],
                     TB, 2.4, 'block', True)
        return h

    if t == 'list_grid':
        L, R = s['left'], s['right']
        lw = (x1 - x0) * 0.22
        lx = x0 + 16
        rx = lx + lw + 46
        rw = x1 - 16 - rx
        box(f'{k}_lh', lx, y, lw, 28, L['header'], DEEP, STK)
        for j, it in enumerate(L['items']):
            box(f'{k}_li{j}', lx, y + 34 + j * 32, lw, 27, it, LIGHT, STK)
        dashframe(f'{k}_rf', rx - 10, y - 6, rw + 20, h - 4)
        box(f'{k}_rh', rx + rw * 0.16, y, rw * 0.68, 28, R['header'], DEEP, STK)
        for j, row in enumerate(R['rows']):
            for i, (cx, cw) in enumerate(C.slots(rx, rx + rw, len(row), 10)):
                box(f'{k}_ri{j}_{i}', cx, y + 34 + j * 32, cw, 27, row[i], LIGHT, STK)
        edge(f'{k}_e', [(lx + lw + 6, y + h / 2), (rx - 14, y + h / 2)], TB, 3)
        return h

    if t == 'scenarios':
        scs = s['scenarios']
        for i, (cx, cw) in enumerate(C.slots(x0 + 20, x1 - 20, len(scs), 22)):
            box(f'{k}_sh{i}', cx, y, cw, 30, scs[i]['name'], DEEP, STK)
            if i:
                edge(f'{k}_sa{i}', [(cx - 20, y + 15), (cx - 2, y + 15)], INK, 1.4,
                     'block', True)
            dw = cw * 0.42
            # 两侧标签在参考图里是竖排窄盒，不是横排
            vbox(f'{k}_sl{i}', cx, y + 44, cw * 0.26, 92, scs[i]['left'], LIGHT, STK, fs=14)
            diamond(f'{k}_sd{i}', cx + cw * 0.29, y + 44, dw, 92, scs[i]['decide'],
                    LIGHT, STK)
            vbox(f'{k}_sr{i}', cx + cw * 0.74, y + 44, cw * 0.26, 92, scs[i]['right'],
                 LIGHT, STK, fs=14)
            box(f'{k}_so{i}', cx, y + 152, cw, 30, scs[i]['out'], LIGHT, STK)
            edge(f'{k}_se{i}', [(cx + cw / 2, y + 137), (cx + cw / 2, y + 151)], INK, 1.6)
        return h

    if t == 'fanout':
        outs = s['outs']
        cw = (x1 - x0) * 0.72
        cx = (x0 + x1) / 2 - cw / 2
        box(f'{k}_c', cx, y, cw, 30, s['center'], DEEP, STK)
        oy = y + 52
        pos = C.slots(x0 + 16, x1 - 16, len(outs), 12)
        bus = y + 42
        edge(f'{k}_stub', [((x0 + x1) / 2, y + 31), ((x0 + x1) / 2, bus)], INK, 1.4, 'none')
        edge(f'{k}_bus', [(pos[0][0] + pos[0][1] / 2, bus),
                          (pos[-1][0] + pos[-1][1] / 2, bus)], INK, 1.4, 'none')
        for i, (ox, ow) in enumerate(pos):
            box(f'{k}_o{i}', ox, oy, ow, 34, outs[i], LIGHT, STK)
            edge(f'{k}_oe{i}', [(ox + ow / 2, bus), (ox + ow / 2, oy - 1)], INK, 1.4)
        return h

    sys.exit(f'未知段型 {t}')


# ---------------------------------------------------------------- 主体
def build(c):
    blocks, stages, rights = c['blocks'], c['stages'], c.get('rights', [])
    heads = c.get('headers', ['研究框架', '研究内容', '研究方法'])
    TOP, GAP = 96, 18
    hs = []
    for b in blocks:
        secs = [sec_h(s) for s in b['sections']]
        hs.append(14 + 34 + 14 + sum(secs) + (len(secs) - 1) * 14 + 14)
    H = TOP + sum(hs) + GAP * (len(blocks) - 1) + 20

    for i, (x, t) in enumerate(zip([58, 430, 820], heads)):
        box(f'hd{i}', x, 28, 120, 34, t, PINK, PINK_S, FS_T, arc=25)

    tops, y = [], TOP
    for bi, b in enumerate(blocks):
        tone = b.get('tone', 'blue')
        TB, TBS, DEEP, LIGHT, STK = TONES[tone]
        h = hs[bi]
        tops.append((y, h))
        dashframe(f'blk{bi}', MID[0], y, MID[1] - MID[0], h)
        tw_ = (MID[1] - MID[0]) * 0.62
        box(f'blk{bi}_t', MID[0] + (MID[1] - MID[0] - tw_) / 2, y + 14, tw_, 34,
            b['title'], TB, TBS, FS_T, fc='#ffffff', arc=8)
        yy = y + 14 + 34 + 14
        for si, s in enumerate(b['sections']):
            yy += draw_sec(f's{bi}{si}', s, MID[0], MID[1], yy, tone) + 14
        y += h + GAP

    # 左栏：竖排方法盒，块间粗箭头推进
    prev = None
    for i, st in enumerate(stages):
        bt, bh = tops[min(st.get('block', i), len(tops) - 1)]
        txt = st['text'] if isinstance(st, dict) else st
        sh = max(len(str(txt)) * (FS_T + 3) + 16, 72)
        sy = bt + bh * st.get('at', 0.35) - sh / 2 if isinstance(st, dict) else bt + 20
        vbox(f'st{i}', RAIL_L[0], sy, RAIL_L[1] - RAIL_L[0], sh, txt, '#ffffff', RAIL_S)
        if i and prev:
            py = prev[0] + prev[1]
            if sy - py > 26:
                barrow(f'st_a{i}', (RAIL_L[0] + RAIL_L[1]) / 2 - 9, py + 8, 18,
                       sy - py - 16, 'south', RAIL_ARROW)
        prev = (sy, sh)

    # 右栏：左向块箭头，箭头体内竖排文字，指入对应块
    for i, rt in enumerate(rights):
        bt, bh = tops[min(rt.get('block', i), len(tops) - 1)]
        txt = rt['text'] if isinstance(rt, dict) else rt
        rh = max(len(str(txt)) * (FS_T + 3) + 26, 80)
        ry = bt + bh * rt.get('at', 0.45) - rh / 2
        chars = list(str(txt))
        if len(chars) * (FS_T + 3) > rh:
            problems.append(f'rt{i}: 竖排 {len(chars)} 字需 {len(chars) * (FS_T + 3)}px'
                            f' > 槽高 {rh:g}px')
        barrow(f'rt{i}', RAIL_R[0], ry, RAIL_R[1] - RAIL_R[0], rh, 'west', RRAIL,
               RRAIL_S, shaft=0.68, head=0.3, text=C.stack(txt), fs=FS_T, width=1.4)
    return int(H)


def main():
    ap = argparse.ArgumentParser(
        description='渲染三栏阶段流程图（matplotlib：PNG 300dpi + 矢量 PDF）')
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
