# Project State 查询职责与返回视图

决策日期：2026 年 10 月 31 日。

## 背景与选择

用户认可将实体定位与关联查询分开的方向，并要求据此制订调整方案。原实施 Plan（`project-state-query-views`）已随旧仓归档；现行查询契约与字段定义以 [Project State 协议](../../../src/trigrams_toolkit/resources/state/PROTOCOL.md) 为准。

现有 `locate` 混合目标定位、直接关联与 Feature 的 Module 文稿展开。`related` 又同时返回实体、关系和重复的 `specs` 入口。查询直接暴露 Registry 对象，使内部定位字段进入 Agent 上下文。

选择按命令分工：`locate` 返回目标本身；`related` 返回直接关联的实体与关系。取消自动沿 Feature 的 Module 展开文稿。相比保留 `relatedArtifacts` 的方案，这一选择消除两条命令之间的重复展开语义。需要模块资料时，调用方沿 `moduleId` 主动查询；已知要查关联时，直接调用 `related` 即可取得文件路径。

## 公共视图

保留 `ok/data` 和现有错误信封。查询视图从 Registry 显式投影，字段如下：

| 对象 | 字段 |
| --- | --- |
| Module | `id`、`kind: core:module`、`name` |
| Feature | `id`、`kind: core:feature`、`name`、`moduleId` |
| Artifact | `id`、`kind`、`title`、可选 `moduleId`、`featureIds` |

`locate` 的 `data` 直接承载上述字段。Artifact 再提供经身份定位得到的绝对 `path`。清单型 Artifact 的路径指向清单文件。Module、Feature 省略 `path`。无 Module 归属时省略 `moduleId`，无 Feature 归属时使用空数组。

`related` 的 `data` 仅包含 `items` 和 `relations`。`items` 使用与 `locate` 相同的字段，每个关联 ID 只出现一次，Artifact 同时提供实际路径。`relations` 沿用 `kind/from/to/source`，保留同一对实体之间的不同关系。

`list` 保留 `data.items`、既有筛选与排序，采用上述基础视图，不解析 `path`。这使枚举不会因文稿失联而失败；需要实际路径时调用 `locate`。三个查询均不返回 `locatorHint` 和 `identityMode`。

Registry 继续保存内部定位与写入信息。注册命令的写入行为与返回契约不在本次调整范围。关系类型名称、Artifact 类型名称以及 `name/title` 的区别沿用现有契约。

## 关联与失败边界

直接关联由登记产生的归属关系和显式额外关系共同组成。`related` 沿用 `both/incoming/outgoing` 及默认双向规则，只遍历一条边，不递归展开。返回目标自身以外的邻接实体。

查询 Feature 时，Module 是直接邻居，但其余模块文稿不是直接邻居。查询 Module 时，声明该 `moduleId` 的 Artifact 都是直接邻居，包括同时归属于 Feature 的文稿。跨 Module 的显式关系按关系端点返回。

`locate` 不查询关联文稿。定位节点或一个正常 Artifact，不因其邻接文稿失联而失败。`related` 仅定位筛选后的邻接 Artifact；无关或方向过滤掉的文稿不应触发定位错误。

目标未注册沿用 `invalid_reference`。本次需要返回路径的 Artifact 无正文或身份重复时，沿用现有 `invalid_reference`、`identity_conflict`，整体查询失败。无关联时返回空 `items` 和 `relations`，不引入部分成功协议。

## 兼容与影响

本次是查询输出的破坏性调整。仓库内消费者与 CLI 同批迁移，不新增旧字段别名或双版本开关。README 和变更日志说明旧字段到新入口的对应关系。正式发布的版本选择沿用项目发布流程，本 Plan 不发布版本。

`plan-toolkit inspect` 的 `specs` 表示 Task 的正式输入，仍保留。它接收新的 `locate` 结果，继续返回已解析路径或逐项错误。历史 Plan、Task、证据和审核记录保持原样。

现有正式协议由 T01 更新为上述行为的详细契约；实现结构、类型签名与输出 schema 由 T01 交付。计划不引入 Registry 迁移、注册方式变化或新的递归查询能力。
