# 项目接入与扩展管理

项目接入与扩展管理由当前 Agent 直接执行。开始前按[全局安装指引](deployment.md)确认四个公共 CLI 与 core Skill 可用。项目装配时，`harness-install install apply` 检查并补齐外部全局 Skill。

## 1. 现状判断与路径分流

确认目标项目根，检查其中的 `.agents/harness.json`、`AGENTS.md`、正式文稿及遗留状态，再选择接入流程。

- **新项目初始化、已有工程首次接入或状态重建**：
  - 适用于尚未接入工具包的新项目、首次接入的既有代码库，或存在需归档重建的旧状态（如退役的旧运行状态、损坏或格式不兼容的 `.agents/harness.json`、损坏的 Registry 或旧 Plan）的项目。
  - 通过 `workbook` Skill 加载 `core:workbook:initialize` 并按其工序直接推进，不创建 Plan。
- **已接入项目增补、同步或移除扩展**：
  - 适用于已完成首次接入、具备正常 `.agents/harness.json` 与项目结构的项目。
  - 不重走 `initialize`，直接按下方步骤管理项目扩展。

## 2. 已接入项目增补扩展

1. **核对当前配置**。查看 `.agents/harness.json` 记录的目标 `agent`（`codex`、`claude-code`、`pi`）、已启用 `extensions` 列表与宿主 `platforms`（`codex`、`claude`、`pi-web`）。增补扩展沿用同一 `agent`。
2. **安装目标扩展 Skill**。为当前 `agent` 安装 `extension-setup-<extension>` 及所需领域 Skill（官方扩展如 `game`、`toolkit-maintenance` 位于 `LINEBARRELS/trigrams-toolkit/extensions/<extension>/skills`，第三方扩展使用其对应来源）：
   ```sh
   npx skills add LINEBARRELS/trigrams-toolkit/extensions/<extension>/skills --skill '*' -a <agent>
   ```
   确认项目 Skill 目录中已出现对应的 `extension-setup-<extension>/SKILL.md`，且无同项目异源同名冲突。
3. **保留既有扩展并装配快照**：`harness-install` 按输入中的 `extensions` 完整集合装配 `.agents/extensions/<extension>/` 快照，不会自动合并旧列表。
   - 构造包含**既有扩展与新增扩展完整扩展列表**的安装输入（输入结构与参数通过 `harness-install install preview --help` 与 `--help schema` 查询）。
   - 运行 `harness-install install preview --input <输入文件>`，审阅变更、冲突及 `projectRoot`，并向用户说明写入范围、目标 `agent` 及可能补齐的全局 Skill；存在本地修改或同名冲突时先确认保留或归档策略并重新预览。
   - 取得确认后运行 `harness-install install apply`，提交预览、确认信息、请求 ID 与期望 revision。
   - 若旧状态需要移档，先停止相关写入并确认项目内相对路径后再运行 `harness-install archive PATH...`；涉及既有正式文稿与目录迁移时，沿用 `initialize` 的迁移清单确认与开工指令。
4. **读取新增 setup 并合并项目约定**。读取本次新安装的 `extension-setup-<extension>/SKILL.md` 及其引用的资料，按领域要求创建文稿与目录。将采用的文档路径、规则与两级术语路由合入根 `AGENTS.md`，保留既有规则与其他扩展条目。合并时保留 `initialize` 模板“公共工具与项目配置”章节的固定文案。
5. **验证与交付**：运行 `handbook validate` 确认全部已启用扩展快照均通过校验；若本次新增或迁移了领域正式成果与关系，运行 `project-state validate` 并用 `project-state locate <Artifact ID>` 核对活动正文可达。最后核对 `AGENTS.md` 新增路径全部真实存在，汇报安装与变更结果。

## 3. 显式同步与扩展移除

- **上游扩展升级后同步快照**：通过 Vercel skills 更新项目扩展 Skill 后，使用保留当前扩展集合（或省略 `extensions`）的输入执行 `harness-install install preview` 与 `apply`，核对本地修改冲突后更新 `.agents/extensions/<extension>/` 快照（显式同步前项目继续读取既有快照）。
- **移除扩展**：从 `extensions` 列表中移除目标扩展名（传 `[]` 清空全部扩展），经 `preview` 与 `apply` 卸载受管快照与安装声明（保留项目自有文稿、正式成果、Plan 与本地修改），随后从 `AGENTS.md` 移除已停用的专属导航条目。
