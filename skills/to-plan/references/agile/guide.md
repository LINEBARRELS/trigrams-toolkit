# Agile 模式规划指引

Agile 模式：以单份 `summary.md` 定义需求、依据、验收、约束与 Stub 清单，不拆分 `tasks/` 目录，不生成 `plan.json`，不使用 `plan-toolkit`。

## 目录与文件布局

沿用项目目录约定；无约定时使用 `docs/plans/<label>/`。

```text
docs/plans/<label>/
  summary.md      # Plan 唯一正文（含 YAML 状态头与全部 Stub 定义）
  S01-result.md   # 执行期由开发维护交付说明、审核追加结论（按 Stub 平铺）
  S02-result.md
  review.md       # 仅多 Stub 时的总体终验结论（单 Stub 时省略）
  evidence/       # 按需仅存放通过验收的最终关键证据
```

## `summary.md` 结构规范

`summary.md` 必须包含 YAML 头声明模式与当前状态：

```yaml
---
plan-type: agile
status: pending
---
```

`status` 取值范围为 `pending`、`doing`、`blocked`、`done`、`cancelled`。

正文按以下 5 个板块组织，使执行者与审核者仅凭 `summary.md` 与明确引用即可独立接手，执行与调度期不再回头查询 `workbook`：

| 板块 | 正文要求 |
| --- | --- |
| `## 需求目标` | 本次工作的核心目标、工作范围与边界 |
| `## 正式依据` | 关联设计文档、Spec、公共契约与维护源的路径及章节链接；列出基于该 Plan 执行工作时必读或选读的完整 principle ID |
| `## 验收标准` | Plan 最终整体验收的必需产物、验证方式和验证标准；审核阶段所需的完整 principle ID 在这里列出 |
| `## 补充约束` | 在当前会话中由用户提出的、针对该 Plan 的附加执行约束；没有则填 “无”，禁止将项目内的通用规则或具体设计内容复制进来 |
| `## Stub 清单` | 用 `### S01 <名称>`、`### S02 <名称>` 划定工作范围边界或关键交付单元 |

## Stub 编写要求

`Stub` 是 Plan 内定义的工作范围边界或关键交付单元。编号为 `S` 加两位数字（如 `S01`、`S02`），在 Plan 内唯一。每个 Plan 至少设置一个 `Stub`。

每个 Stub 块应写清以下信息：

- **内容范围与产物位置**：本 Stub 的具体交付内容、目标文件路径或交接位置。
- **前置依赖（按需）**：若依赖其他 Stub 的完整结果，或存在共享文件写竞争，显式指明执行顺序。
- **补充 principle（按需）**：若本 Stub 有额外的相关 principle 需在工作前读取，列出完整 principle ID。
- **附加验收与审核**：
  - 调度者默认在一个 Stub 完成后派发一次针对该 Stub 内容的独立审核；
  - 若所选 `workbook` 要求某 Stub 声明附加审核或特殊条件审核，应在本 Stub 块内显式写明各检查点、阶段验收判据及对应必读审核 `principle` ID（如 `programming-review` 下的原则）。

## Plan 检测与修订

文稿完成后派发 subagent 进行内容核验：

1. **自包含且精炼**：核对所选 `workbook` 的必要工序、附加规则与 principle ID 已落盘到 `summary.md`，执行期无需再查 `workbook`；删除大段复抄、跨 Skill 通用规则或瞬时工作区状态。
2. **验证有效且必要**：每项交付要求与关键失败风险均有可区分合格与不合格的验证方式；Stub 依赖无环且无共享写冲突遗漏。
3. **引用可达**：核对 `summary.md` 中引用的本地文件路径、章节定位与 Artifact ID 真实有效。

修订已开始（`doing`）的 Agile Plan 时，核对已有进展与 `Sxx-result.md`，保留有效产物与已确认的历史审核结论；若修订影响已通过审核的 Stub，在 `summary.md` 中写明需重验的范围。

交付时向用户汇报 Plan 目录、检测结论、规划期可能发现的问题以及设计或规划内容缺项。
