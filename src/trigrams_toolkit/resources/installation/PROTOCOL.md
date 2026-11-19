# 项目资源装配与归档协议

[harness-install 命令](commands.json)使用[输入 schema](cli.schema.json)和[安装记录 schema](installation.schema.json)。查询 `harness-install install preview --help schema` 和 `harness-install install apply --help` 获取字段与命令细节。

## 项目根与资源来源

在目标项目根目录运行装配和归档命令。帮助（`-h`／`--help`）与版本（`-v`／`--version`）可在任意目录查看。预览在项目根按 `agent` 查找 `extension-setup-<extension>`，读取其 `assets/extension.json`。受支持的名称为 `codex`、`claude-code`、`pi`。省略 `agent` 时沿用已装配记录的选择，首次默认 `codex`。Codex 与 Pi 共享 `.agents/skills/`，Claude Code 使用 `.claude/skills/`，支持链接或同内容复制。发现同名异源时先统一来源再预览。

Vercel skills 安装全局 core Skill 和项目扩展 Skill。全局 `principles`、`workbook` 各自携带 core 资料。`agent` 决定从哪个宿主查找 Skill，adapter 的 `platforms` 单独指定（`codex`、`claude`、`pi-web`）。

`extensions` 是希望保留的完整扩展集合。省略时沿用原选择，显式 `[]` 清空全部扩展。增补时列出已选扩展和新增项。本地开发可显式提供绝对路径 `packages`，使用 `extension.json` 或 `resources.json`。其扩展名称须与所选集合一致，可附带 core 源以验证 includes。

## 快照与归属

[版本 2 项目记录](examples/installation.json)保存目标 `agent`、`stateRevision`、`extensions`（含 `version`）、`platforms` 和受管路径。快照位于 `.agents/extensions/<extension>/`，包含 `extension.json` 以及完整的 `principles/`、`workbooks/` 材料及其配套文件。handbook 与 Project State 读取记录登记的快照。上游 Skill 升级后，在下一次显式装配前继续消费项目中的版本。项目自有资料继续来自 `docs/resources.json`，核心类型与 adapter 随 Python 包发布。

每个受管文件保存 `contentDigest`（已安装字节的 SHA-256）。安装和卸载都核对基线，冲突路径在预览显示。卸载保留项目自有文稿和额外文件。声明的 `install` 需要合法相对源、目标与平台；目标归对应扩展所有。Vercel 管理 Skill 目录、宿主 Skill 入口和 `skills-lock.json`。宿主角色 adapter 由安装器从 Python 包复制到 `.codex/agents/`、`.claude/agents/` 或 `.pi/agents/`。

## 预览、应用与回执

`install preview` 只读，可离线运行。[预览输入](examples/install-preview-input.json)声明需要的扩展和平台。结果包含 `projectRoot`、基准修订号、规范化参数、扩展来源、逐路径新增／更新／移除项与冲突。相同版本与相同字节再次装配时，只有修订记录更新，回执的 `changed` 为 `false`。

`install apply` 使用[应用输入](examples/install-apply-input.json)中的完整预览与 `confirmedBy`，并要求 `--request-id req_ID` 和 `--expected-revision N`。命令先核对当前项目根与预览的 `projectRoot`，再持有项目安装锁核对修订号、重建预览并复查来源和目标。来源或目标有变化时刷新预览。最近一次成功的原样请求直接返回已提交回执，同 ID 异参数报 `request_conflict`。

首次装配、增补和同步在项目写入前检查目标 agent 的全局 Skill 目录。缺少 `archify` 或 `smell-check` 时，使用 `npx` 执行官方安装命令，可能访问网络并写入该目录。补齐失败时保留受管文件和项目记录，修复后可重试。纯卸载和已提交请求的回执重放可离线运行。

最近一次操作保存在 `.harness/previous/`。复制文件原件在 `backup/`，处置与目标登记在 `receipt.json`。写入失败时回退已尝试的文件并记录 `rolled_back`，随后可以重试。安装记录最后写入。遇到强制终止或断电留下的 `applying` 回执时，依据回执和原件恢复后再生成预览。升级装配协议前完成或恢复旧操作，升级后沿用版本 2 项目记录，重新生成预览并使用新的请求 ID。

## 明确路径归档

`archive PATH [PATH ...]` 接受至少一个项目内相对路径。工具先校验全部路径存在、互不重叠且位于当前项目根，禁止选择 `.git`、`.harness-archive` 及其内部路径。父目录解析后须仍位于项目内。叶节点为符号链接时只移动链接本身。

全部校验通过后，工具使用 `rename` 将选定路径原样移入项目根的 `.harness-archive/<UTC批次>/`，保留原相对路径。该命令可离线运行。它将文件视为不透明内容，状态恢复由迁移流程处理。成功返回归档目录 `archive` 与原项目相对路径列表 `paths`。

已有项目先停止相关写入并核清范围，用本命令归档待替换的旧运行状态与受管生成材料；项目文档与工具按迁移清单直接移入 `docs/archives/` 分类目录。归档后在干净的活动位置重新安装材料、登记架构身份并按实际产物验收；旧完成状态不作为本次状态依据。
