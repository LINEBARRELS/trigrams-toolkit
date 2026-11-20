# Python 验证工具链

本文件提供 Python 项目主流验证工具的分工与官方文档入口。项目既有工具栈的识别、配置格式、规则名称与校验命令，均以目标项目实际安装版本及对应官方文档为准。

## 主流验证工具分工与官方文档

已有对应类别的工具时优先复用，不无故更换现有生态。

| 验证层次 | 推荐工具 | 负责范围 | 官方文档 |
| --- | --- | --- | --- |
| 静态类型检查 | Pyright / mypy | 公开签名完整注解、`None` 收窄、`NewType`、`Protocol`、`Final`、`TypedDict` 与未等待协程检查 | [Pyright Configuration](https://microsoft.github.io/pyright/#/configuration) · [mypy Documentation](https://mypy.readthedocs.io/) |
| 语法与质量 Lint | Ruff | 可变默认参数、裸 `except`、异常原因链、`is None` 判别、上下文资源管理、异步阻塞、规模与复杂度 | [Ruff Rules](https://docs.astral.sh/ruff/rules/) |
| 模块依赖图与分层边界 | `import-linter` / `tach` | 跨包无环依赖、分层单向依赖、禁止绕过公开入口深层导入 | [Import Linter](https://import-linter.readthedocs.io/) · [Tach](https://docs.gauge.sh/) |
