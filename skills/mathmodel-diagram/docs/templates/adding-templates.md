# 新增一个模板

> 只在"某类图会反复画"时才做模板；一次性的图直接按 `docs/guides/authoring.md` 用 matplotlib 手写更快。

每个模板 = 一个渲染脚本 + 一份说明 + 一份示例 + 一张预览 + SKILL.md 索引里的一行。照下面的契约做，新模板与已有模板在用法上完全一致（同样的 CLI、同样的容量校验、同样的自检口径）。

## 一、先标定，再画

模板的观感来自几何精度，**不要目测坐标和配色**。从参考图提取的可行做法（`roadmap-5band` 就是这么来的）：

```python
# 1) 盒子：把"非描边"区域连通域化，逐个填洞后取矩形外接框 + 中位填充色
stroke = (lum < 205) | ((sat > 45) & (lum < 235))
lab, n = ndimage.label(~stroke)
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    m = ndimage.binary_fill_holes(lab[sl] == i)      # 填掉文字造成的孔
    if m.sum() / m.size > 0.88: ...                  # 只保留矩形区域

# 2) 边框/分带线：整行整列扫描"笔画覆盖率"，虚线取 40–70% 区间
# 3) 配色：对参考图做颜色普查（量化到 8 级）取占比最高的若干种
```

字号用实测反推：量一行已知字数的像素宽度 ÷ 字数 = 单字宽 ≈ 字号。**不要假设"标题一定比正文大"**——学术模板常是扁平字号。

## 二、渲染脚本契约

放 `code/templates/<template_id>.py`，一律基于 `code/common.py` 的基元层
（`Recorder` + `draw_*` + `guard` + `save_figure`），CLI 固定：

```bash
python3 code/templates/<template_id>.py content.json -o out.png    # 出 PNG 300dpi + 同名矢量 PDF
python3 code/templates/<template_id>.py content.json --check       # 只校验不写
```

必须做到：

1. **写文件前逐槽容量校验**（`common.check_text_fits` / `fit()`），超框直接非零退出并报出
   具体槽位与预算，例如 `b2_data: "……" 宽 224px > 可用 212px（约 13 个汉字）`。
   字宽模型：CJK/全角 = 字号 px，半角 = 字号/2，行高 = 字号 + 3。可用宽 = 槽宽 − 8。
   透明文字标签的高度可放宽到 1.4 倍（无边框，溢出不难看）。
2. **数量可变的组用均分**：`common.slots(a, b, n, gap)` 把区间等分，槽位随数量自动变窄/变矮；
   在文档里写明每组的允许区间，并在脚本里 `sys.exit` 拦截越界。
3. **几何常量集中在文件头**，内容一律来自 JSON，禁止把文案写进脚本。坐标系 1 px = 0.01 inch、
   y 轴向下（`setup_canvas`），标定值可原值使用。
4. 手动断行用 `"\n"`，同时接受字符串或字符串数组；竖排文字逐字堆叠（`common.stack`）。
5. 高度自适应的模板用 `Recorder` 先排队指令，画布尺寸定了再 `REC.canvas(w, h)` 一次回放。

## 三、matplotlib 画法的四个坑

几何问题由脚本内置的字宽校验兜住，但渲染层有几处画法需要注意（均已在现有模板验证）：

| 现象 | 原因 | 做法 |
|---|---|---|
| 箭头端点"压住"盒子 | 端点正好落在边界上，视觉上被框线吞掉 | 所有连接器端点离盒边 **1 px**（`anchor()` 已内置） |
| 一分多/多合一像一捆斜线 | N 条独立折线各走各的中线 | 画"竖线+横母线+分支"三段式：母线用 `head='none'` 的箭头 |
| 大段文字与色块糊在一起 | 背景块与文字同 z 层 | 指令按"背景→框→文字→箭头"顺序 emit，`Recorder` 回放即层序 |
| PDF 里中文变曲线 | 默认 pdf.fonttype=3 | `common.py` 已全局设 `pdf.fonttype=42`，勿在模板里覆盖 |

模板刻意不校验紧密堆叠的行列间距与"同族尺寸是否对齐"（前者是刻意排版，后者机器判族必然
跨族误报）——这两项交给眼睛，见 `docs/guides/self-check.md`。

## 四、与手写路径的关系

模板渲染脚本本质就是"把手写绘图指令参数化"，基元与样式速查表在 `docs/guides/authoring.md`，
两边必须保持一致（同一套 `common.py` 基元、同一套字宽模型、同样的端点外移 1px 约定）。

## 五、交付清单

```
code/templates/<template_id>.py
docs/templates/<template_id>.md      # 语义 + 槽位字数预算（两节，带目录）
examples/<template_id>/example.json  # 填满的真实示例，不要占位符
examples/<template_id>/preview.png   # 用本模板渲染器导出的 1:1 预览
SKILL.md                             # 在模板索引表加一行
```

`docs/templates/<template_id>.md` 必须包含：每个字段的**汉字预算**（用脚本算，不要手估）、
数量允许区间、以及"哪些槽位是并列/汇流/对比"的语义约定——语义放错比字数超框严重得多。

## 六、验收

1. 用示例 JSON 渲染出 PNG，**肉眼逐带核对**（截图必须是画布本身）；
2. 造一份"每组取边界数量"的压力配置再渲一次，确认版式不散；
3. 若是复刻某张参考图，用像素差分比对（`np.abs(ref-render)` 聚类定位差异区域），
   把残留差异写进说明的"已知近似"一节。
