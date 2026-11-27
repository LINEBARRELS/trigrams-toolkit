# Agile 模式规划指引

Agile 模式：以单份 `summary.md` 定义需求、依据、验收、约束与 Stub 清单，不拆分 `tasks/` 目录，不生成 `plan.json`，不使用 `plan-toolkit`。

## Plan 目录结构与文件布局

沿用项目目录约定；无约定时使用 `docs/plans/<label>/`。

```text
docs/plans/<label>/
  summary.md              # Plan 唯一正文（含 YAML 状态头与全部 Stub 定义）
  review.md               # Plan 总体终验结论与问题索引
  findings/               # 按需：仅当 Plan 总体终验提出跨 Stub 问题时创建
    R01.md
  evidence/               # 按需仅存放通过验收的最终关键证据
  S01/                    # 执行期开工时按需创建
    result.md             # 开发维护：产物清单与验证依据
    handoff.md            # 开发按需维护：交接与遗留（无特殊交接时不创建）
    stub-review.md        # 审核维护：各轮结论、验证摘要与问题索引
    findings/             # 审核按需维护：每条 Rxx 独立文档（无问题时不创建）
      R01.md
```

## `summary.md` 模板与填写规范

`summary.md` 应直接展开本次生效的规则内容，不通过链接回指 `workbook`。

```markdown
---
plan-type: agile
status: pending
---

# <Plan 标题>

## 工作内容

<本次工作的核心目标和工作范围。100字以内>

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
<schedule-rule>
</schedule-rule>

执行规则：
<exec-rule>
</exec-rule>

审核规则：
<review-rule>
</review-rule>

## 补充约束（按需）

<仅记录用户在当前会话中针对本 Plan 显式提出的附加约束；按需创建该章节>

## Stub 清单

<`Stub` 是 Plan 内按可独立验证的成果范围切分的交付单元，编号为 `S` 加两位数字（如 `S01`、`S02`），Plan 至少设置一个 `Stub`。>

### S01 <Stub 名称>

- **内容范围与产物**：<具体交付边界、目标文件路径或交接位置；若适用多阶段调度，简要标明各阶段产出边界>
- **前置依赖**（按需）：<在该 Plan 内的前置依赖 Stub 编号>
- **补充 principle**（按需）：<仅本 Stub 独有的、在工作时需读取的 principle ID>
- **验收要点**（按需）：<仅本 Stub 独有的局部验收条目或定向补充验证>
```

### workbook 附加规则标签注入

创建 Plan 时扫描所选 `workbook` 中可能存在的 `<schedule-rule>`、`<exec-rule>`、`<review-rule>` 标签，按当前工作内容与项目环境进行条件判定，整合并入进 `summary.md`：

1. **条件求值**：无属性标签始终命中；相邻同名标签通过 `if="<条件>"`、`else-if="<条件>"`、`else` 构成互斥条件组，自上而下仅命中首个满足条件的分支（标签不允许嵌套）。
2. **原文注入**：仅将命中标签内的正文**原文复制**进 `summary.md` 对应插槽，同时剥离原标签 `if` / `else-if` / `else` 属性（Plan 内只保留已裁决的确定规则）。
3. **同类合并**：按读取顺序持续地将 `workbook` 中命中的标签内容按分类附加到 `summary.md` 的对应标签内，以空行分隔。
4. **空项省略**：未命中任何内容的插槽与 title 直接省略；三个插槽均为空时省略整个 `## 附加调度规则` 章节。

## Plan 检测与修订

文稿完成后派发独立 subagent 对 Plan 进行质检：

1. **内容完整、精准**：核对 `workbook` 的附加规则标签内的原文与附加 principle ID 已正确落盘到 `summary.md`，执行期无需再查 `workbook`。
2. **验证有效且必要**：每项交付要求与关键失败风险均有可区分合格与不合格的验证方式。
3. **Stub合理切分**：Stub 声明的相互依赖无环，各 Stub 的内容保持正交，避免因范围越界或重叠而导致的脏读、脏写。
4. **引用可达**：核对 `summary.md` 中引用的文件路径、章节定位等内容真实有效。

修订已开始（`doing`）的 Agile Plan 时，核对已有进展与各 `Sxx/` 下的交付、审核记录，保留有效产物与已确认的历史审核结论；若修订影响已通过审核的 Stub，在 `summary.md` 中写明需重验的范围。

最终向用户汇报 Plan 目录、Plan 质检结论、规划期可能发现的问题以及设计或规划内容缺项。
