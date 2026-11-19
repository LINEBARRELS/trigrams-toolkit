# CLI 输出与资料加载边界

决策日期：2026 年 10 月 27 日。

## 背景与依据

用户要求减少 `plan-toolkit inspect` 的上下文开销，使 `handbook load` 可一次读取多个 ID，并明确退役 principle 的 `includes` 支持，只保留 workbook 的递归加载，同步 schema、测试和说明。

此前 core、toolkit-maintenance 与 game 的原则拆解已使现行原则成为独立条目。本次核对未发现实际 principle 声明 `includes`，但 handbook 的 schema、加载器和测试仍保留该能力。

## 选择

- principle 是加载叶子，头信息只接受 `description`；声明 `includes` 时返回 `invalid_schema`。workbook 的 `includes` 可引用 workbook 或 principle，继续递归、去重并检查缺失引用与循环。
- `handbook load ID [ID ...]` 合并各入口的资源集合。新增稳定的 `selectedIds` 数组；单参数调用保留原 `selected` 字符串。任一入口失败时整次失败。
- 歧义错误通过 `error.conflicts` 返回可直接重试的完整候选 ID，复用已有解析结果。
- `inspect` 默认返回精简视图，显式传入 `--full` 时返回原完整结构。默认结果省略正文、重复路径与空集合，保留状态、有效说明、阻因、工作目录及 Task 的 Spec 定位错误。
- 常规 Skill 调用直接使用 `inspect`，所需正文沿源路径按需读取。完整选项由工具帮助与契约说明，不在各调用处重复介绍。
- 默认输出切换前完成消费者的字段适配；候选验证通过后更新公共 CLI，再启用 handbook 的新增批量调用。

## 影响与承接

旧的自建 principle 若声明 `includes`，升级后会被拒绝；其必要组合应由 workbook 声明。不提供静默忽略或自动迁移。当前仓库没有该类正文迁移负担，外部项目未纳入本次调查。

无参数 inspect 的输出会改变，当前消费者应迁移到默认精简结果。原完整响应由 `--full` 保留，普通调用不承担重复正文的上下文开销。

本轮同时补齐歧义候选；目录文本筛选、额外 Markdown 输出格式与普遍补充帮助示例保留为后续讨论项。

接口细节、调用方切换和验收已随原实施 Plan 归档于旧仓；本记录保存取舍，现行机器字段与命令约束以 [Plan 协议](../../../src/trigrams_toolkit/resources/plan/PROTOCOL.md) 与 [Handbook 协议](../../../src/trigrams_toolkit/resources/handbook/PROTOCOL.md) 为准。
