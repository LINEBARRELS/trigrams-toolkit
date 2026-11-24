---
description: 规划或检查扩展源码目录布局、清单文件位置与包内资源链接时使用。
---
# 将扩展资产自包含于 Setup 的 assets 包根

每个扩展的唯一维护源与包根应固定为 `extensions/<name>/skills/extension-setup-<name>/assets/`，所有可装配资源应封闭在该目录内。

布局与打包边界应满足以下要求：
- 仓库 `toolkit.json` 的 `extensions.<name>.manifest` 与 `skills` 应分别精确指向上述 `assets/extension.json` 与 `extensions/<name>/skills`，且不得为符号链接。
- 扩展包内不应出现 `_runtime`、`contracts/runtime`、`verification/`、`.exe`、`.zip`、生成物缓存目录（如 `.agents`、`.git`、`__pycache__`），也不应在 `assets/extension.json` 之外散落 `extension.json`、`resources.json`、`provider.json`，或在 `resourceRoots` 内放置 `resource.json`/`yaml`/`yml`、`package.json`。
- `resourceRoots` 只声明真实存在的 `principles` 或 `workbooks` 子目录；`assets/` 内所有 Markdown 相对链接应封闭解析于 `assets/` 内，确保快照装配后零断链。
