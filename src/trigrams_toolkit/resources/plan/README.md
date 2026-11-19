# Plan Toolkit

`plan-toolkit` 读取 Plan 文稿，编译调度快照，维护 Plan、Task 与 Stub 的当前状态。

## 编写与检查

先编写 `summary.md` 和 `tasks/T01/task.md`。Task 声明 installs、fills、uses 中的 Stub 编号与名称；完整要求保存在 summary 的 Stub 块。完整格式通过 `to-plan` Skill 获取。

```powershell
plan-toolkit validate docs/plans/P01 --sync
plan-toolkit validate docs/plans/P01
plan-toolkit get-task docs/plans/P01
plan-toolkit inspect docs/plans/P01 T01
plan-toolkit mark docs/plans/P01 doing
plan-toolkit mark docs/plans/P01 T01 doing
plan-toolkit mark docs/plans/P01 T01 done --note "框架已审核且下游可读取"
plan-toolkit block docs/plans/P01 T02 --reason "等待接口确定；从序列化适配继续"
plan-toolkit cancel docs/plans/P01 T03 --reason "范围已撤销"
```

从目标项目根运行上面的命令。`PLAN` 是项目内的明确目录，相对路径从项目根解析。`TASK` 来自 Task 目录编号，省略时状态命令修改 Plan 自身。可在任意目录用 `-h` 或 `--help` 查看帮助，用 `-v` 或 `--version` 查看工具包版本。

`validate --sync` 建立或更新 plan.json 的定义快照，并保留已有状态、note 和 reason。新增 Task 为 pending。同步会检查格式、名称、生产者、阶段顺序、Task / Stub 混合依赖环及完成路径。候选不合规时不替换原状态。

成功时检查退出码为 0、`ok: true`、`data.valid: true`；`data.changed` 表示是否写入。普通 validate 只读，缺少状态或快照过期时失败。计划修订后再次显式同步，不手工维护 JSON 声明。

## 获取当前工作

`get-task PLAN` 返回 `data.status`、`data.ready[]` 与 `data.waiting`。ready 每项含 Task id 与 task.md 的绝对 path。waiting 按 Task 编号列出 Task 前置、Stub 安装条件或人工阻因。空清单不代表 Plan 完成。

候选 Task 为 pending 或 rework，dependsOn 均 done，uses 和 fills 的 Stub 均已 installed 或 filled。doing、blocked、done、cancelled Task 不重复派发。Plan 为 blocked、done 或 cancelled 时不提供候选。真实共享文件竞争与工作树整合仍由调度者判断。

`inspect PLAN` 默认返回精简状态：Plan 根目录、整体状态和按 Task ID 索引的状态表，并保留有值的说明、工作目录、阻因及 Stub 名称和阶段。`inspect PLAN TASK` 返回 Task 的绝对路径、状态、关联 Stub 名称和阶段，以及 Spec 入口。Task 定义与正文从该路径读取，Stub 正文从 summary 的对应块读取。没有 plan.json 时 inspect 可预览 pending 状态，不写文件；调度与状态变更应先完成同步。

inspect 的 `--full` 返回原完整视图，包含调度声明、重复路径和空集合；Task 查询还包含正文、目录文件与 Stub 正文。两种视图均不返回 ready，可开工项仍用 get-task 查询。完整字段由 [PROTOCOL.md](PROTOCOL.md) 维护。

Spec 按 ID 调用包内 state 定位服务，与 project-state locate 使用同一业务实现。Task 查询的 `data.specs[]` 可含单条 error，外层成功不代表全部 Spec 已定位。整体查询不定位 Spec。

## 状态联动

Stub 状态为 `uninstalled → installed → filled`。同一 Stub 的安装与装填由不同 Task 承担。安装 Task done 后进入 installed；装填 Task done 后进入 filled。uses 只等待框架，等待完整行为使用 dependsOn 指向装填 Task。

mark 接受 pending、doing、rework、done。block 和 cancel 写入 blocked 或 cancelled，并要求非空 reason。每次动作替换目标当前说明，未提供的 note 或 reason 清除，重复相同动作返回 changed 为 false。Task 转为 doing、rework 或 done 时都会核对前置。

状态写入返回本次目标状态，发生阶段变化时另返回 `data.stubChanges`，例如 `{"S01":"installed"}`。Task 与 Stub 在同一次原子替换中更新；不级联改变其他 Task 或 Plan。

生产者返工或撤销后，Stub 会重新计算。若会破坏 doing / done 下游，则拒绝写入并列出受影响 Task。取消必要生产者会使 validate 和 get-task 报告计划不可完成，修订相应安排后同步。Plan done 要求全部 Task 为 done 或 cancelled，全部保留 Stub 为 filled。

写命令使用普通文件锁与原子替换；失败不覆盖原文件。sync 不静默删除已开工 Task，不修改 doing / done Task 的调度声明，也不修复损坏的状态。完整字段、响应与错误见 [PROTOCOL.md](PROTOCOL.md)。

原先无 Stub 的精简状态可通过显式 validate --sync 补齐快照并保留进展。更早的冻结文稿或版本化状态仍返回 unsupported_plan，应通过 initialize 归档并重建。

## 验证

从仓库根运行：

```powershell
python -m unittest discover -s tests/runtime -p "test_plan_*.py" -v
python -m unittest discover -s tests/runtime -p "test_cli_help.py" -v
python -m unittest discover -s tests/runtime -p "test_atomic_files.py" -v
```
