# 从零手写示意图（matplotlib）

模板之外的图（算法流程、模型架构、实验设计、机制示意）直接写一段 Python：
`import common` 取基元，在像素坐标系里摆盒子、连箭头。产物 PNG 300dpi + 矢量 PDF。

- [一、骨架](#一骨架)
- [二、基元速查](#二基元速查)
- [三、中文字宽预算](#三中文字宽预算)
- [四、连接器写法](#四连接器写法)
- [五、四个必踩的坑](#五四个必踩的坑)

## 一、骨架

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code").resolve()))   # 按脚本实际位置调整
import common as C

W, H = 1000, 700                     # 画布 px；1 px = 0.01 inch，y 轴向下
fig, ax = C.setup_canvas(W, H)

C.draw_box(ax, 80, 60, 240, 70, text="输入数据", fill="#F5F5F5",
           stroke="#8E9AAF", ls=C.DASH, width=1.2, fs=16, radius=5)
C.draw_box(ax, 380, 60, 240, 70, text="核心算法", fill="#D6E4F0",
           stroke="#4C72B0", width=1.2, fs=16, radius=5)
C.draw_arrow(ax, [(321, 95), (379, 95)])                    # 端点离盒边 1 px

png, pdf = C.save_figure(fig, "out")                        # out.png + out.pdf
print(png, pdf)
```

**先排栅格再写图元**：定死画布、列基线、步距；同族同宽同步距（用 `C.slots(a, b, n, gap)`
等分），数量可变的组一律公式化，不要手抄坐标。

## 二、基元速查

| 指令 | 用途 | 关键参数 |
|---|---|---|
| `draw_box` | 圆角盒（默认图元） | `fill/stroke/ls/width/radius/fs/fc/text/grad=(c1,c2)` |
| `draw_rect` | 直角矩形（色块、面板底、背景带） | `stroke=None` 做纯背景块 |
| `draw_text` | 无边框文字（栏外标签、图题） | `halign/valign/bold=False` |
| `draw_dashed_rect` | 虚线分组框（点线传 `ls=C.DOT`） | 只画框不装文字 |
| `draw_flag` | 右向五边形旗标（阶段标签） | `tip` 调尖角深度，`text_dx` 微调文字 |
| `draw_block_arrow` | 粗块箭头（阶段推进、分发） | `direction=east/west/south/north`、`shaft/head` 调杆厚头长、`text` 可入箭头 |
| `draw_double_arrow` | 双向箭头（互相印证、对照） | `fill/stroke` 灰系 |
| `draw_diamond` | 菱形（判断分支） | `text` 短词 |
| `draw_hexagon` / `draw_cylinder` | 机制/枢纽、数据库 | 语义点缀，勿滥用 |
| `draw_brace` | 大括号（归组说明） | `x,y,w,h` 定开口范围 |
| `draw_arrow` / `draw_curved_arrow` | 正交折线 / 平滑弧线连接器 | 见第四节 |
| `Recorder` | 指令排队回放（高度自适应时用） | `REC.emit(kind, **kw)` → `REC.canvas(w,h)` |

配色沿用模板体系：主蓝 `#4C72B0`、深蓝边 `#3b547f`、浅蓝底 `#eef6fd/#D6E4F0`、
苔绿 `#55A868`、赭橙 `#DD8452`、岩石灰 `#8E9AAF`、炭墨 `#2F353B`；同图 ≤4 个色系。
描边宽度成体系：普通盒 1–1.5，强调盒 2，主流程线 1.2–2，粗块箭头填充无边。

## 三、中文字宽预算

`C.text_width(text, fs)`：CJK/全角 = fs px，半角 = fs/2；行高 = fs + 3。
`C.check_text_fits(text, box_w, fs)` 返回 `(ok, 需求宽)`，可用宽 = 盒宽 − 8。

- 16 px 字号下 240 px 宽盒每行最多 14 个汉字；**超预算就手动 `"\n"` 断行**，
  等长两行比自动换行体面得多；
- 竖排标签用 `C.stack("数据层")` 逐字堆叠（每字一行，字符正立）。**不要**用
  `rotation=90` 旋转整段中文——横排字体会歪且行距失控；
- 图元摆好后先跑一遍 `C.guard(problems)` 式校验再保存，别靠肉眼在成品图里找溢出。

## 四、连接器写法

`draw_arrow(ax, pts, ...)` 吃一条点列：

- **端点离盒边 1 px**（`anchor()` 的约定），正好落边会像被框"咬住"；
- 一分多 / 多合一画成 **"竖线 + 横母线 + 分支"**：母线段用 `head='none'`，
  各分支段单独带箭头；不要画成 N 条独立斜线；
- 折线走向用 `C.ortho_points(p_from, p_to, mid_y)` 生成"垂-平-垂"，`mid_y` 手动
  给可以避免折线穿盒；跨距大、需绕行的用 `via` 点列全接管；
- 循环/反馈回路用 `draw_curved_arrow`（Catmull-Rom 过拐点），粗弧配 `head_size≈2–4`，
  否则箭头巨大；
- 每根箭头画之前想清楚语义（谁到谁、单向双向、扇入扇出）；说不出含义的箭头不要画。

## 五、四个必踩的坑

1. **y 轴向下**：`setup_canvas` 已翻转，与 drawio/图像像素习惯一致；若自加
   `ax.invert_yaxis()` 会翻回两次，文字全部倒序。
2. **层序 = 绘制顺序**：后画的压住先画的。背景块 → 框 → 文字 → 箭头；箭头要最后画，
   否则会被盒填充盖住端点。
3. **`fill=None` 与 `stroke=None`**：无边框文字块用 `draw_text`，不要 `draw_box` 配
   白填充——导出 PDF 后白块会盖住底下的连线。
4. **保存后别再改图**：`save_figure` 即终态。要迭代就改脚本重跑（脚本才是源，
   PNG/PDF 是产物），不要在图像上手工修补。

写完过一遍 `docs/guides/self-check.md` 的九区盘点再交付。
