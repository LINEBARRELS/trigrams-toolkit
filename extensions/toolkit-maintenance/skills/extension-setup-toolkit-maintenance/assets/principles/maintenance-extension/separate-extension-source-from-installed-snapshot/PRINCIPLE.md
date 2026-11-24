---
description: 区分扩展仓库源码修改、版本发布对齐与目标项目快照装配验证时使用。
---
# 区分扩展维护源码与项目安装快照双态

扩展存在“仓库维护态”与“项目快照态”两种独立生命周期，修改与验证应分别对齐各自权威入口，避免将源码改动误认为项目快照已生效。

处理双态边界时应遵守以下准则：
- 仓库维护态以 `extensions/<name>/` 与 `toolkit.json` 为权威源，通过 `scripts/verify_toolkit.py` 校验源码闭包，通过 `tasks.py check-release` 核对版本声明一致。
- 项目快照态固定于目标项目 `.agents/extensions/<name>/` 并由 `.agents/harness.json` 记录基线，通过 `handbook validate` 与 `handbook list`/`load` 校验实际可发现性。
- 刷新或移除项目快照应显式经由 `harness-install` 执行 preview、apply 与 verify，不应手工覆盖 `.agents/extensions/`；移除扩展只清理受管材料，保留项目自有成果、Plan 与知识。
