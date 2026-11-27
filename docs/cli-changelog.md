# CLI 更新记录

四个公共 CLI 共用 `trigrams-toolkit` Python 包。版本号以 `pyproject.toml` 为准。

## 0.6.0

- `harness-install install preview` 移除 `platforms` 输入，扩展清单的 `install` 条目也移除 `platforms`。升级时从输入及自有扩展清单删除该字段。目标宿主通过 `agent` 指定。
- CLI 包移除 Codex、Claude 和 Pi Web 宿主适配器。安装器仍可读取含 `platforms` 的版本 2 `.agents/harness.json`。重新预览并应用装配会清理旧受管适配器。存在本地修改时，预览会报告冲突并保留文件。[安装协议](../src/trigrams_toolkit/resources/installation/PROTOCOL.md)

## 0.5.3

- 这是独立发版前最后一个共用版本。后续 CLI 版本从这里递增。此前的 CLI 变更见[工具包更新记录](../CHANGELOG.md)。
