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

## `summary.md` 模板与填写规范

`summary.md` 须自包含全部规划期决策，确保工作执行与调度中不再回查 `workbook`。

```markdown
---
plan-type: agile
status: pending
---

# <Plan 标题>

## 需求目标

<本次工作的核心目标、工作范围与明确边界。>

## 正式依据

- **关联文档与数据源**：
  - `<相对路径>#<章节锚点>`（写作时可采用 Markdown 链接）：<用途说明>
- **执行期 principle**：
  - `<完整 principle ID>`（必读 / 选读与触发条件）

## 验收标准

- **必需产物与验收判据**：
  - <可区分合格与不合格的产物、行为或状态要求>
- **验证方式**：
  - <具体验证命令、测试场景或核查方法>
- **审核期 principle**：
  - `<完整 principle ID 或 scope>`

## 附加调度规则（按需）

调度规则：
<schedule-rule></schedule-rule>
执行规则：
<exec-rule></exec-rule>
审核规则：
<review-rule></review-rule>

## 补充约束（可选）

<仅记录用户在当前会话中针对本 Plan 显式提出的附加约束；按需创建该章节>

## Stub 清单

### S01 <Stub 名称>

- **内容范围与产物**：<具体交付边界、目标文件路径或交接位置；若适用多阶段调度，简要标明各阶段产出边界>
- **前置依赖**（按需）：<依赖完成的 Stub 编号，或因共享文件写竞争须串行的对象>
- **补充 principle**（按需）：<仅本 Stub 独有的额外 principle ID>
- **验收要点**（按需）：<仅本 Stub 独有的局部验收条目或定向补充验证>
```

### Plan 编写约束

1. **内容精炼**：严禁将项目通用规则、既有设计正文复抄进 `summary.md`，标有“（按需）”的条目不适用时直接省略。
2. **Stub 编号**：`Stub` 是 Plan 内定义的工作范围边界或关键交付单元，编号为 `S` 加两位数字（如 `S01`、`S02`），在 Plan 内唯一且至少设置一个。

## Plan 检测与修订

文稿完成后派发 subagent 进行内容核验：

1. **内容完整**：核对所选 `workbook` 的注入规则与附加 principle ID 已落盘到 `summary.md`，执行期无需再查 `workbook`。
2. **验证有效且必要**：每项交付要求与关键失败风险均有可区分合格与不合格的验证方式；Stub 依赖无环且无共享写冲突遗漏。
3. **引用可达**：核对 `summary.md` 中引用的本地文件路径、章节定位与 Artifact ID 真实有效。

修订已开始（`doing`）的 Agile Plan 时，核对已有进展与 `Sxx-result.md`，保留有效产物与已确认的历史审核结论；若修订影响已通过审核的 Stub，在 `summary.md` 中写明需重验的范围。

最终向用户汇报 Plan 目录、Plan 检测结论、规划期可能发现的问题以及设计或规划内容缺项。
