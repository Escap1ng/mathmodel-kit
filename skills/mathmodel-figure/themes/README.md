# 主题目录

图表主题的**声明式定义**：把「颜色只承担身份 / 基准 / 方向 / 层级四种职责」这组规则从代码里提出来，
变成可替换、可校验的数据。

| 文件 | 作用 |
|---|---|
| `theme.schema.json` | 主题契约（JSON Schema Draft 2020-12）：字段名是契约，色值是内容 |
| `nature.theme.json` | 默认主题（Nature 标准）。`plot_style.py` 的内置常量与它逐值一致 |
| `<你的主题>.theme.json` | 自己加的：复制 `nature.theme.json` 改名，改色值即可 |

## 怎么用

```bash
# 按名使用内置主题（默认就是 nature）
python3 code/tools/render_template.py grouped-bar --theme nature

# 用自定义主题文件
python3 code/tools/render_template.py grouped-bar --theme ~/my-theme.theme.json

# 查看可用主题
python3 code/tools/render_template.py --list-themes
```

渲染时主题会被复制到工作区 `scripts/theme.json`，所以：

- **工作区是自包含的**——脚本连同主题一起交给别人，任何人重跑都得到同一套颜色；
- **改工作区里的 `scripts/theme.json` 即可覆盖配色**，不需要动仓库里的模板；
- 仓库内的 `plot_style.py` 也按「同目录 `theme.json` → 内置默认主题」的顺序查找，因此**按同一模块自绘的图**
  同样受主题控制（把 `theme.json` 放在脚本旁边即可）。

## 适用范围

- **生效**：共用 `code/style/plot_style.py` 的图表模板，以及按该模块自绘的图；
- **不生效**：配色写在自己脚本头部的模板（多为结构定制图），以及 `mathmodel-diagram` 的 5 个示意图模板
  （其配色是版式语义的一部分）。这些仍可在**工作区副本**里改，只是不受主题文件统一控制。

## 校验

```bash
python3 code/tools/validate_theme.py --all             # 校验 themes/ 下全部主题
python3 code/tools/validate_theme.py my-theme.theme.json
```

校验项：结构合法（对 `theme.schema.json`）、色值为 6 位十六进制、`name` 合法且不与已有主题重名。
CI 会在每次 push / PR 时跑 `--all`，所以自定义主题写错会在提交时就被拦住。
