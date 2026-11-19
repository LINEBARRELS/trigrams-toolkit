---
name: principle-maintenance
description: 根据项目问题与证据提炼、修订项目 principle 候选草稿，经用户审定后调用 handbook 入库维护唯一 principle 来源。
metadata:
  harness-toolkit-type: workflow
---

# principle-maintenance

接收项目问题、证据输入、适用范围、已有 principle、资料来源及相关 Plan 目录或交付证据，维护项目 principle。用于新增或修订项目原则。

## 必要工作流程

1. **事实调查**：核对实施事实与决策问题。需要核实当前事实时调用 `how`；缺少历史原因时调用 `why`。提供项目上下文、已有证据、资料来源与可用的实际 Plan 目录。资料不足部分保留未知，不阻断已有证据分析。
2. **提炼原则候选草稿**：
   - 比较目标、结果、偏差与适用前提，提炼跨任务复用的判断准则候选。
   - 拟定英文小写连字符 `scope` 与 `name`，将候选草稿写入 `docs/research/principle-drafts/<scope>/<name>.md`（有真实候选时创建）。正式身份为 `project:principle:<scope>/<name>`；修订已有原则时沿用原身份。
   - 草稿采用完整原则格式：YAML 头仅包含 `description`；正文包含判断准则、适用条件、必要理由、例外与来源。草稿属于研究记录，不参与正式索引与发现。
   - 按正式入口位置核对正文中的相对引用与附件，修正引用并安排附件位置，再提交审定。CLI 原样写入正文，不改写引用或搬运附件。
3. **修订影响分析**：
   - 修订或特化已有原则时，在正文注明对象、条件与保留要求。调用 `effect`，传入前后正文、原资源 ID、项目上下文与可用的实际 Plan 目录，分析受影响使用方、未完成工作与重验需求。影响不能确认的范围单列，连同草稿提交用户审定。
4. **用户审定与入库调用**：
   - 将草稿、路径中的拟定 `scope` 和 `name` 与已有影响分析提交用户审定。已有明确批准则继续；未获批准的草稿保持待审。
   - 新增原则审定时调整身份的，按确认的身份调整草稿路径，重新核对正式位置下的引用与附件；正文有变更时交用户审定。已有原则需要变更身份时，先明确迁移与旧入口处理方式，不用 `--replace` 创建新身份。
   - 用户明确批准后，从草稿路径取得 `scope` 和 `name`，在目标项目根逐条调用入库命令：
     - 新增原则：`handbook import-principle FILE --scope SCOPE --name NAME`
     - 修订已有原则：`handbook import-principle FILE --scope SCOPE --name NAME --replace`
     - `FILE` 为草稿路径（相对调用目录解析或绝对路径）。CLI 自动维护项目原则资源声明并发布到 `docs/knowledge/principles/<scope>/<name>/PRINCIPLE.md`，同时保留源草稿。
   - **结果判据与异常恢复**：
     - 成功判据为退出码 0 且响应 `ok: true`，返回 `resourceId`、`entryPath` 与 `operation`（`created` 或 `updated`）。
     - 失败时退出码为 1 且 `ok: false`。若发生写入阶段失败，核对 `error.current` 指向的 `packageWritten` 与 `entryWritten`。正文未写入时保留草稿，排查原因后重试原命令；正文已写入或状态未知时，核对声明与正文实际文件，再决定是否带 `--replace` 重试。
5. **校验与交付**：
   - 运行 `handbook validate`，核对退出码 0、`ok: true` 且 `checkedSources` 包含更新的项目原则来源。
   - 交付实际入库结果、校验输出、受影响范围及待审草稿（未批准条目）。在途 Plan 修订由后续已授权的规划工作承接。
