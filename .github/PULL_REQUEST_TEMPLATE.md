## 这个 PR 做了什么

<!-- 一句话说明动机（为什么改），而不是复述改了什么 -->

## 所属子模块

<!-- 对应 CONTRIBUTING.md 的四个子模块，用于分流与指定评审方 -->

- [ ] M1 文档与示例
- [ ] M2 代码与模板
- [ ] M3 测试与验证

## 类型

- [ ] 新增模板
- [ ] 改进既有模板
- [ ] 文档 / 示例
- [ ] 修复缺陷
- [ ] 其他（请说明）

## 自查清单

- [ ] 已在本地运行 `python -m compileall -q skills`
- [ ] 新增/修改的模板已登记进对应 `manifest.json`（注册表是单一事实源，无需改 CLI 与 CI）
- [ ] 示意图模板已附 JSON Schema，且必备字段与代码中的 `need()` / `c['key']` 访问一致
- [ ] 示意图模板的 `example.json` 填满真实内容，字数预算为**实测**值（不是手估）
- [ ] 预览图已更新
- [ ] 索引文档已同步（`figure-catalog.md` 或示意图 `SKILL.md` 的模板索引表）
- [ ] 未提交生成物（工作区目录、`.aux`、PDF/PNG 产物）
- [ ] 内容中没有编造的数据或文献
- [ ] 涉及 Stable 契约（CLI 参数与退出码、注册表字段、主题契约字段）的改动已注明，并已按需更新 `CHANGELOG.md`

## 验证

<!-- 贴出你实际跑过的命令与关键输出，例如：
python code/tools/render_template.py <id> --project /tmp/check
python code/tools/validate_content.py --all
-->

```bash
```

## 相关 Issue

Closes #
