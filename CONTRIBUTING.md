# 参与维护

八卦 Trigrams toolkit 的贡献入口使用仓库 Issue 与 PR，日常讨论围绕具体场景、行为和验证证据展开。开发环境与源码验证见[开发与接入](docs/getting-started.md)和[维护与发布](docs/maintenance.md)。

## 提出改动

- 缺陷：提供工具包版本、平台、复现步骤、预期结果与实际结果。
- 改进：说明使用场景、当前障碍和希望改变的行为。
- 文档：指出错误位置与正确表述；小范围修正可直接提交 PR。
- 新 Skill 或扩展：先说明现有能力为什么不能覆盖，以及新能力的维护位置。

涉及真实凭据或项目私有数据的问题，通过团队现有私密渠道联系仓库维护者。Issue、日志与附件只保留复现所需信息。

## 实施与验证

1. 阅读根目录 [AGENTS.md](AGENTS.md) 与改动范围内的 Skill、脚本手册。
2. 创建围绕单一目的的分支；Agent 创建的分支使用 `codex/` 前缀。
3. 在维护源修改内容，同步更新用户能看到的说明。
4. 运行与行为变化对应的检查，并在 PR 中记录命令、结果和未验证范围。
5. 提交 PR，说明问题、结果、影响范围与升级影响。

| 改动范围 | 验证要求 |
| --- | --- |
| README、说明与配图 | 校对本地链接和图片；检查浅色、深色与窄屏可读性 |
| Skill、模板或安装资源 | 资源校验、资料加载及受影响的项目材料验证 |
| 公共工具 | Python 类型、业务与协议验证；涉及运行材料时执行隔离包验收 |
| 校验与发布脚本 | 对应行为测试，以及源码和隔离包校验 |
| Project State | Python 类型、身份／锁／路径行为测试、Skill 示例与标准入口验收 |
| 打包与 CI | wheel／sdist 构建、包内资源闭包与 uv 隔离工具安装 |

命令统一见仓库[维护与发布说明](docs/maintenance.md#验证)。脚本行为变化补充能证明结果的测试；纯文字与图片改动不要求新增代码测试。

## `.gitignore` 约定

本仓库自身的开发与维护同样基于 Trigrams toolkit。为避免本地环境差异污染开源仓库，所有维护者与贡献者遵循根目录 [.gitignore](.gitignore) 的以下划分：

- **纳入版本管理**：`.project-state/state.json` 仅保存逻辑实体身份、相对路径提示与关系，与文稿 YAML 头中的 `artifact-id` 配对生效，启用后应随文稿正常提交。
- **始终忽略运行锁与回滚状态**：`.project-state/*.lock.sqlite*`、`**/.plan.lock`、`.harness/`（含带本机绝对路径的 `receipt.json` 与备份）及 `.harness-archive/` 属于运行期与本机恢复产物，严禁提交。
- **本仓忽略本地 dogfooding 装配产物**：通过 Vercel skills 与 `harness-install` 在本仓本地装回的 `.agents/skills/`、`.agents/extensions/`、`.agents/harness.json`、`.claude/`、`.codex/`、`.pi/` 与 `skills-lock.json` 仅用于本地开发环境，不纳入本仓版本控制——既避免污染 Vercel skills 的仓库发现路径，也避免与 `extensions/`、`src/trigrams_toolkit/resources/adapters/` 形成双份副本或把单一宿主偏好锁死在公共仓库中。
- **普通使用方项目**：接入 Trigrams toolkit 的业务仓库按 [initialize `.gitignore` 模板](skills/workbook/workbooks/initialize/assets/templates/.gitignore) 配置；业务项目通常应提交 `.agents/harness.json` 与 `.agents/extensions/` 快照以锁定团队扩展版本，仅忽略运行锁、回滚目录与本地 Skill 安装目录。

## 审核与合并

审核者核对改动是否解决所述问题、规则是否仍有唯一来源、验证是否覆盖影响范围。影响已安装项目的改动还应说明迁移与回退路径。

PR 模板收集交接信息，不替代仓库内的 Plan / Task 协议。维护者在检查通过后合并；有其他可用维护者时，由未参与实现的人审核。

版本变化记录在 [CHANGELOG.md](CHANGELOG.md)。文档与品牌调整先记入未发布章节，不自动提升工具包或 CLI 版本。

## 来源与许可

提交原创内容，或注明引入内容的来源与许可。第三方材料保留原有声明，更新 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。原创内容采用 MIT，见 [LICENSE](LICENSE)。
