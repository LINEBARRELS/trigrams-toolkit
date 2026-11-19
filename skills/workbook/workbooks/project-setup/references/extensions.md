# 扩展管理

本说明对应[主 workbook](../WORKBOOK.md#原子工作目录)的**工作 4（扩展管理）**。扩展层作为完全可选项，叠加在已就绪的核心底座（工作 1–3）之上。

## 前置护栏与寻址规则

- **核心底座前置检查**：独立调用工作 4 前，先确认 `.agents/harness.json` 与 `AGENTS.md` 已存在；若缺失，先向用户说明并补齐必需的工作 1–3，再叠加扩展。同一会话中已确认同时做工作 1–3 与工作 4 时，可先完成工作 1–3，或在工作 4 安装扩展 Skill 后合并一次 `harness-install` 装配以减少重复确认。
- **直接按路径读取 setup**：所有 `extension-setup-<extension>` 均设为仅手动触发（`disable-model-invocation: true`）。执行工作 4 时，由当前 Agent 直接按项目路径读取该 Skill 正文：
  - 通用目录：`.agents/skills/extension-setup-<extension>/SKILL.md`
  - Claude Code：同步检查 `.claude/skills/extension-setup-<extension>/SKILL.md`
- **完整集合语义**：`harness-install` 的 `extensions` 参数接收本次期望保留的**完整扩展集合**（省略时沿用已有选择，传入 `[]` 清空全部扩展）。上游扩展 Skill 更新后，在显式运行 `harness-install` 同步前，`handbook` 与 `project-state` 继续读取既有快照。开发调试或旧来源缺失时，可通过绝对路径 `packages` 指定来源根。

## 安装或增补扩展

1. **确认当前配置**：读取 `.agents/harness.json` 中的 `agent`、`extensions` 与 `platforms`，增补扩展沿用同一 `agent`。
2. **安装扩展 Skill**：在项目根目录运行：
   ```sh
   npx skills add LINEBARRELS/trigrams-toolkit/extensions/<extension>/skills --skill '*'
   ```
   使用 Claude Code 时附加 `-a claude-code`；第三方扩展替换为对应来源。确认目标目录下已出现 `extension-setup-<extension>/SKILL.md` 且无异源同名冲突。
3. **装配扩展快照**：构造包含**既有扩展与新增扩展完整列表**的输入，按[统一装配门禁](core-config.md#统一装配门禁preview--apply)运行 `harness-install install preview → apply`，生成 `.agents/extensions/<extension>/` 快照及 `extension.json` 中 `install` 声明的附加受管材料。
4. **按 `extension-setup-<extension>` 四段正交结构叠加增量**：直接读取项目内的 `extension-setup-<extension>/SKILL.md` 及正文引用的配套资料，按其前三段依次落实增量（第 4 段仅在用户明确要求工作 5 时读取）：
   - **1. 资源结构与依赖检查**：核对快照、必需领域 Skill、领域类型／关系，并运行 `handbook validate`。
   - **2. 特定目录路径**：在核心 `docs/` 骨架上按需补齐该扩展约定的领域目录。
   - **3. 项目级文档补充与新增**：对现有核心文档（如 `PRODUCT.md`、`DESIGN.md`、`AGENTS.md`）合并领域增量，并按需创建扩展专属项目级文档（如 `docs/GAME-VISUALS.md`）；确保 `AGENTS.md` 导航只列入实际存在的路径。

## 显式同步与移除扩展

- **上游升级同步快照**：通过 Vercel skills 更新项目扩展 Skill 后，使用保留当前集合（或省略 `extensions`）的输入按[统一装配门禁](core-config.md#统一装配门禁preview--apply)运行 `preview → apply`，核对本地修改冲突后刷新 `.agents/extensions/<extension>/`。
- **移除扩展**：从 `extensions` 列表中移除目标扩展名（传 `[]` 清空全部扩展），运行 `preview → apply` 卸载受管快照与安装声明（保留项目自有文稿、正式成果、Plan 与本地修改）；再参照该扩展 `extension-setup-<extension>` 第 3 段的移除清理项，从 `AGENTS.md` 删除已停用的专属导航与术语路由。
