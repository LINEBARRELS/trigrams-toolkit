# Plan 调度与当前状态契约

## 命令

| 命令 | 效果 |
| --- | --- |
| `validate PLAN [--sync]` | 检查格式、声明一致性、混合依赖与完成路径；--sync 编译快照 |
| `get-task PLAN` | 读取当前可开工 Task 与等待原因 |
| `inspect PLAN [TASK] [--full]` | 默认读取精简状态；--full 返回完整交接视图 |
| `mark PLAN [TASK] STATE [--note TEXT]` | 写入 pending / doing / rework / done，联动 Stub |
| `block PLAN [TASK] --reason TEXT` | 写入 blocked 与原因 |
| `cancel PLAN [TASK] --reason TEXT` | 写入 cancelled 与原因 |

PLAN 为目录，TASK 为 tasks/<TASK>/task.md 的目录编号。省略 TASK 的状态命令修改 Plan。可在任意目录用 `-h` 或 `--help` 查看帮助，用根命令的 `-v` 或 `--version` 查看版本。validate 与 get-task 不接受 TASK，只有 validate 接受 --sync，只有 inspect 接受 --full。

## 文稿定义

summary.md 保存总体要求与 Stub 详情；Task YAML 保存 dependsOn、specs、workspace、installs、fills、uses，工作要求写正文。Task ID 为 T 加数字。依赖和 Spec 列表缺省为空，workspace 可省略。未知头字段、重复键及重复引用会报错。

installs、fills、uses 为数组，每项只含 id 和 name，名称与 summary 中相同 ID 的标题一致。新计划的每个 Task 显式写这 3 项，未使用时为空数组。无 Stub 的既有精简文稿可省略，读取时按空数组处理；含 Stub 的 Plan 中不允许省略。

Stub ID 为 S 加数字，在 Plan 内唯一。summary 的块格式为：

```markdown
<!-- harness:stub S01 -->
### S01 库存服务
安装与装填要求、交接位置及各阶段验收。
<!-- /harness:stub S01 -->
```

块不嵌套，首标题固定为三级标题、编号、名称；标题后有非空要求正文。Task 仅声明 ID 与名称，不复制详情。每个 Stub 恰有一个安装者与一个不同的装填者。

dependsOn 等待指定 Task done。uses 等待 Stub installed 或 filled。fills 隐含等待该 Stub installed，不必再写 uses；完整行为依赖通过 dependsOn 指向装填 Task。安装者依赖自身安装结果、同 Task 安装并装填同一 Stub、未知生产者与依赖环均不合规。

## 快照与状态

[plan.schema.json](plan.schema.json) 定义 plan.json。根包含 status、tasks、stubs。每个 Task 记录 status、dependsOn、installs、fills、uses；引用列表只保存 ID。Stub 记录 name 与 status，不保存正文或重复的生产者字段。反向生产关系从 Task 声明推导。

Plan 与 Task 状态为 pending、doing、rework、blocked、done、cancelled。有信息时保存 note；blocked 和 cancelled 要求非空 reason，其他状态不接受 reason。状态动作替换目标当前说明，未提供的说明清除，不改动声明快照。

Stub 状态为 uninstalled、installed、filled。安装者未 done 时为 uninstalled；安装者 done 且装填者未 done 时为 installed；两者均 done 时为 filled。保存的 Stub 状态应与 Task 状态一致。

validate --sync 首次建立快照，后续保留既有 status、note、reason，从文稿同步声明并推导 Stub 状态。新增 Task 为 pending，新增 Plan 为 pending。删除非 pending Task、修改 doing / done Task 的调度声明、丢弃已有交付阶段的 Stub 时返回 progress_conflict。删除尚未开工的 pending Task 可在无剩余引用时同步。

同步前先验证已有文件格式与进展一致性。候选通过当前进展与完成路径检查后才写入，不修复损坏状态。普通 validate、get-task 和状态写入要求快照已存在且与文稿相同；缺少时返回 missing_state，过期时返回 definition_out_of_sync。inspect 在没有状态文件时可预览 pending 状态。

## 依赖校验与就绪

所有 dependsOn 边，以及每个 fills / uses 指向安装者的等待边，合并成 Task 图。校验完整图的环，包括已完成 Task 的声明，错误返回实际环中的 Task 链。只检查显式 dependsOn 不足以判定合规。

在拓扑顺序中模拟全部未撤销 Task 的完成。结构演算允许 blocked 临时阻因解除；不把 blocked 当永久死锁。cancelled 不完成前置，也不产生 Stub 阶段成果。仍不可达的 Task 或无法装填的 Stub 导致 unreachable_plan。

doing / done Task 的前置应已满足。生产者回退或撤销会重算 Stub；若破坏这些下游则返回 invalid_progress，不自动回退其他 Task。block / cancel 可记录异常，但由此产生的完成路径缺口应在继续调度前修订。

get-task 内部复用上述检查，不额外调用 Spec 定位。只返回 pending / rework 且 Task、Stub 前置均满足的 Task，按 Task ID 排列。blocked 单列人工阻因，doing、done、cancelled 不进入候选。Plan 为 blocked、done、cancelled 时 ready 为空。空候选不等于完成，也不代表文件修改可并行。

mark doing、rework、done 核对同一套 Task 与 Stub 前置，不能绕过阶段顺序。Task 新转为 doing 时，Plan 应为 pending、doing 或 rework；整体受阻或结束时先恢复 Plan，已有 doing 记录不级联改变。Plan done 要求全部 Task 为 done 或 cancelled，全部保留 Stub 为 filled。Task 变动不级联改变其他 Task 或 Plan；取消 Plan 不修改 Task 或删除交付。

## 文件与项目定位

业务命令从目标项目根运行。相对路径以进程当前目录为基准。Plan 的实际路径须在当前项目内，Git worktree 从各自的根读取 Plan 状态。

Task inspect 将同一项目根与 specs ID 交给 Project State 定位服务，读取该根的 Registry 与正文。单条失败保存在 data.specs[].error，不改变外层成功响应；调用方核对 path 或 error。默认与完整视图均保留每项定位结果。整体 inspect 不定位 Spec。Task 查询的 data.stubs 只包含 installs / fills / uses 引用的块；默认每项含 name、status，--full 另含 body。

读命令不写文件。validate --sync 和状态命令先预检，再在 .plan.lock 的普通文件锁内重新读取，原子替换 plan.json。Task 与 Stub 一次提交。锁冲突返回 lock_busy，不自动合并；锁文件保留，进程退出后操作系统释放锁。预检失败不创建新锁文件。

## 输出

成功输出一行 UTF-8 JSON：`{"ok":true,"data":{...}}`，退出 0；参数、业务或 IO 失败退出 1。帮助与版本输出纯文本。

| 调用 | data |
| --- | --- |
| validate | valid 为 true，changed 表示是否写入；普通检查为 false |
| get-task | status 为 Plan 状态；ready 每项含 id、绝对 path；waiting 按 Task ID 列出阻因 |
| inspect PLAN | directory、status、按 Task ID 索引的 tasks；有值时保留 Plan 与 Task 的 note、reason，Task 的 workspace、非空 blockers，以及非空 stubs 的 name、status |
| inspect PLAN TASK | id、绝对 path、status；有值时保留 note、reason、workspace、非空 blockers、关联 stubs 的 name、status，以及非空 specs 的原定位结果或 error |
| inspect PLAN --full | 原完整状态、stubs、tasks、directory、summary；Task 记录含声明数组、绝对 path 与 blockers，保留空集合 |
| inspect PLAN TASK --full | id、完整当前记录、绝对 path、directory、body、contents、关联 Stub 的 name、status、body、specs 定位与 blockers，保留空集合 |
| 状态写入 | changed、directory、本次目标状态与说明；Task 另含 id；阶段变动时另含 stubChanges |

waiting 的前置阻因格式为 `{"type":"task或stub","id":"编号","required":"done或installed"}`；人工阻因为 `{"type":"manual","reason":"原因"}`。stubChanges 为 Stub ID 到新状态的映射，不附送完整任务表。

inspect 默认省略调度声明数组、空集合与重复路径。整体查询只保留 Plan 根目录，不重复 Task 路径或 summary 路径；Task 查询保留 task.md 的精确绝对 path，省略 directory、body、contents 和 Stub 正文。任务定义和正文从 `tasks/<Task ID>/task.md` 读取，Stub 正文从 `summary.md` 对应块读取。两种视图均不返回 ready；可开工项仍由 get-task 计算。

协议失败返回 `{"ok":false,"error":{"code":"...","message":"...","issues":[...]}}`。issues 提供字段路径、Task、Stub 或依赖链；IO 失败仅有 code 与 message。调用方检查退出码与 ok，validate 另检查 data.valid。

原先无 Stub 的精简状态只允许显式 --sync 补齐，并保留已有状态。更早的版本化状态或冻结文稿返回 unsupported_plan，应通过 project-setup 归档重建。

plan.schema.json 的身份为 urn:harness:plan。[commands.json](commands.json) 是 6 个命令的清单。
