#!/usr/bin/env python3
"""problem-flow：问题分析流程图 / 系统架构图（matplotlib 渲染 → PNG 300dpi + 矢量 PDF）。

    python3 code/templates/problem_flow.py content.json -o out.png
    python3 code/templates/problem_flow.py content.json --check   # 只校验容量

样式契约（承自数模论文「流程图专项规范」）：圆角扁平方框，三类模块——
algo 核心算法（浅蓝 #D6E4F0 / 主色A 实线边）、config 配置与辅助（极淡灰 #F5F5F5 /
岩石灰虚线边）、output 输出成果（浅灰蓝 #EBF2FA / 主色A 实线边）；文字炭墨
#2F353B 居中。主流程炭墨实线箭头，次要数据流（反馈/参数传递）岩石灰虚线箭头；
连接线一律正交折线，端点离盒边 1 px，严禁斜线直连与横穿模块。

JSON 结构：
  canvas:  {"w": 800, "h": 650}          # px，1 px = 0.01 inch
  font_size: 16                          # 可选，默认 16 px（≈11.5 pt，≥9 pt 红线）
  modules: [{"id", "text", "kind": "algo|config|output",
             "x", "y", "w", "h", "icon": ""}]     # x/y 为盒左上角；icon 可选单字符
  edges:   [{"from", "to", "primary": true,
             "from_side": "bottom", "to_side": "top", "via": []}]
           # side ∈ top/right/bottom/left，默认 bottom→top；via 给中间拐点全接管折线
布局建议：串行自上而下；并行分支均分多列、同宽同高；总分结构顶层居中、底层收拢。
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import common as C                                            # noqa: E402

TXT = '#2F353B'
FS_DEFAULT = 16
LINE_H = FS_DEFAULT + 3
ICON_H = 22                       # icon 行占位（px）
RADIUS = 5                        # 圆角 ≈3.5 pt

STYLE = {
    'algo':   dict(fill='#D6E4F0', stroke='#4C72B0', ls=None),
    'config': dict(fill='#F5F5F5', stroke='#8E9AAF', ls=C.DASH),
    'output': dict(fill='#EBF2FA', stroke='#4C72B0', ls=None),
}
PRIMARY = dict(color=TXT, ls=None)
SECONDARY = dict(color='#8E9AAF', ls=C.DASH)

problems: list[str] = []
REC = C.Recorder()


def need(d, key, where):
    if key not in d:
        sys.exit(f'缺少字段 {key}（{where}）')
    return d[key]


def anchor(m, side):
    """盒某边的中点，沿出射方向外移 1 px（端点压在边线上视觉上像被框吞掉）。"""
    cx, cy = m['x'] + m['w'] / 2, m['y'] + m['h'] / 2
    if side == 'top':
        return cx, m['y'] - 1
    if side == 'bottom':
        return cx, m['y'] + m['h'] + 1
    if side == 'left':
        return m['x'] - 1, cy
    return m['x'] + m['w'] + 1, cy


def route(p0, s0, p1, s1, via):
    """两端点 + 出入边方向 → 正交折线点列。via 非空时全接管。"""
    if via:
        return [p0] + [(float(a), float(b)) for a, b in via] + [p1]
    x0, y0 = p0
    x1, y1 = p1
    vert = s0 in ('top', 'bottom')
    if vert and s1 in ('top', 'bottom'):
        if abs(x0 - x1) < 0.5:
            return [p0, p1]
        my = (y0 + y1) / 2
        return [p0, (x0, my), (x1, my), p1]
    if not vert and not s1 in ('top', 'bottom'):
        if abs(y0 - y1) < 0.5:
            return [p0, p1]
        mx = (x0 + x1) / 2
        return [p0, (mx, y0), (mx, y1), p1]
    if vert and s1 in ('left', 'right'):          # 垂出 → 平入
        return [p0, (x0, y1), p1]
    return [p0, (x1, y0), p1]                     # 平出 → 垂入


def check_module(m, fs):
    mid = m.get('id', '?')
    if m['kind'] not in STYLE:
        sys.exit(f'模块 {mid}: kind 必须是 algo/config/output，收到 {m["kind"]!r}')
    lines = C.lines_of(need(m, 'text', mid))
    usable = m['w'] - 8
    for ln in lines:
        ok, wneed = C.check_text_fits(ln, m['w'], fs)
        if not ok:
            problems.append(f'{mid}.text: "{ln[:12]}…" 宽 {wneed:.0f}px > 可用 {usable:.0f}px'
                            f'（约 {int(usable // fs)} 个汉字/行）')
    hneed = len(lines) * (fs + 3) + (ICON_H if m.get('icon') else 0) + 8
    if hneed > m['h']:
        problems.append(f'{mid}.text: {len(lines)} 行需高 {hneed:.0f}px > 盒高 {m["h"]:g}px')


def build(c):
    canvas = c.get('canvas', {})
    W = float(canvas.get('w', 800))
    H = float(canvas.get('h', 650))
    fs = float(c.get('font_size', FS_DEFAULT))

    modules = {m['id']: m for m in need(c, 'modules', '顶层')}
    for m in modules.values():
        check_module(m, fs)
        if m['x'] < 0 or m['y'] < 0 or m['x'] + m['w'] > W or m['y'] + m['h'] > H:
            problems.append(f"{m['id']}: 越出画布 {W:g}×{H:g}")

    for m in modules.values():
        s = STYLE[m['kind']]
        REC.emit('box', x=m['x'], y=m['y'], w=m['w'], h=m['h'], text=None,
                 fill=s['fill'], stroke=s['stroke'], width=1.2, ls=s['ls'],
                 fs=fs, fc=TXT, bold=True, radius=RADIUS)
        if m.get('icon'):
            REC.emit('text', x=m['x'], y=m['y'] + 4, w=m['w'], h=ICON_H,
                     text=m['icon'], fs=fs + 2, fc=TXT, bold=False)
            REC.emit('text', x=m['x'], y=m['y'] + ICON_H, w=m['w'],
                     h=m['h'] - ICON_H - 4, text='\n'.join(C.lines_of(m['text'])),
                     fs=fs, fc=TXT, bold=True)
        else:
            REC.emit('text', x=m['x'], y=m['y'], w=m['w'], h=m['h'],
                     text='\n'.join(C.lines_of(m['text'])), fs=fs, fc=TXT, bold=True)

    for e in need(c, 'edges', '顶层'):
        a, b = e.get('from'), e.get('to')
        if a not in modules or b not in modules:
            sys.exit(f'边 {a}->{b}: 端点 id 不存在')
        p0 = anchor(modules[a], e.get('from_side', 'bottom'))
        p1 = anchor(modules[b], e.get('to_side', 'top'))
        pts = route(p0, e.get('from_side', 'bottom'), p1, e.get('to_side', 'top'),
                    e.get('via'))
        st = PRIMARY if e.get('primary', True) else SECONDARY
        REC.emit('arrow', pts=pts, color=st['color'], width=1.2, ls=st['ls'],
                 head='block', head_size=6)

    if c.get('title'):
        REC.emit('text', x=0, y=8, w=W, h=fs + 8, text=c['title'], fs=fs, fc=TXT,
                 bold=True)
    return W, H


def main():
    ap = argparse.ArgumentParser(
        description='渲染问题分析流程图/系统架构图（matplotlib：PNG 300dpi + 矢量 PDF）')
    ap.add_argument('content', help='content JSON path')
    ap.add_argument('-o', '--out', default=None, help='output path（后缀忽略，一律出 png+pdf）')
    ap.add_argument('--check', action='store_true', help='only run the capacity check')
    a = ap.parse_args()

    c = json.loads(pathlib.Path(a.content).read_text(encoding='utf-8'))
    W, H = build(c)
    C.guard(problems)
    print(f'✓ 容量检查通过（画布 {W:g}×{H:g}）')
    if a.check:
        return
    fig, _ = REC.canvas(W, H)
    png, pdf = C.save_figure(fig, C.output_path(a.out, a.content))
    print(f'✓ 已写出 {png}（300 dpi）与 {pdf}（矢量），共 {len(REC.ops)} 个图元')


if __name__ == '__main__':
    main()
