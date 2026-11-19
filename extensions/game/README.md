# 游戏研发扩展（game）

可选提供方 `game` 提供游戏领域的玩法设计与程序开发工作方法（workbook）、设计原则（principle）与角色契约。通过 core 的 workbook 与 principles 能力按描述或稳定 ID 选择。

## 提供资源概览

### 工作方法（Workbooks）

| workbook | 稳定 ID | 工作范围 |
| --- | --- | --- |
| [玩法设计](skills/extension-setup-game/assets/workbooks/gameplay-design/WORKBOOK.md) | `game:workbook:gameplay-design` | 玩法内循环切片、规则结算定义、交互反馈设计与 Gameplay Spec 编制 |
| [游戏程序开发](skills/extension-setup-game/assets/workbooks/game-programming-development/WORKBOOK.md) | `game:workbook:game-programming-development` | 消费玩法 Spec，按两阶段流程组织架构安装、规则装填、表现装配、调试支撑与渲染专项开发 |

### 原子化原则（Principles）

原子化判断标准位于 `skills/extension-setup-game/assets/principles/`，按四个 scope 组织：
- `gameplay-rules`：实体状态域、规则结算完整性、状态不变式与转移判定。
- `gameplay-experience`：玩家目标对齐、操作反馈、节奏控制与试玩诊断。
- `gameplay-composition`：跨机制桥梁 Spec、依赖解耦与组合契约维护。
- `runtime-evidence`：运行证据环境绑定、复现场景隔离、性能预算对照与交付物核验。

---

## 架构理念：“扩展声明工作重点，项目落地准则与工具”

为了通用支持 Godot、Unity、Unreal 以及自研 C++ 引擎等多样化技术栈，`game` 扩展遵循控制反转（IoC）与关注点分离（SoC）架构：**扩展层负责在工作方法（Workbook）中描述任务切片与验证重点；具体项目则根据自身引擎与技术栈，定义衡量准则并自备可执行工具链**。

### 1. 证据插槽理念（Evidence Slots Pattern）

在设计上，`game-programming-development` 将各种特化 Coding Task 的交付关注点抽象为四类通用的**证据插槽（Evidence Slots）**理念，不硬编码具体引擎命令行或特定文件路径：

| 证据插槽理念 | 对应 Task 分流 | 核心关注重点 | 下游用途与交接价值 |
| --- | --- | --- | --- |
| **规则确定性** (`logic-determinism`) | **规则装填 Coding** | 纯规则结算、状态转移确定性、边界不变式 | 供 `delivery-review` 对照 `R-xx` 规则验收；作为回归基线，保障联机同步与存档一致性。 |
| **交互反馈** (`interaction-feedback`) | **表现装配 Coding** | 视听反馈出现时机、操作手感、音画动效对齐 | 供 `delivery-review` 对照 `F-xx` 验收体验；确认美术与音效资源挂载完整且表现无迟滞。 |
| **调试复现** (`debug-reproducibility`) | **调试支撑 Coding** | 独立隔离环境、边界秒级复现、轻量调试入口 | 供后续复杂任务快速直达目标状态，免除前置长流程负担；供自动化测试脚本复用。 |
| **渲染预算** (`render-budget`) | **渲染专项 Coding** | 图形管线负载、DrawCall/Overdraw 合批、GPU 耗时 | 供 `delivery-review` 对照性能预算裁决；作为版本集成基准，防止图形改动导致掉帧与显存劣化。 |

### 2. 项目侧配套基础设施与自主权

接入 `game` 扩展的具体项目，拥有完全的架构自主权，按需在项目自身内部维护：

1. **项目自建准则 (Project Principles)**：
   - 定义项目特有的断言标准与预算阈值（如特定平台的帧率底线、DrawCall 上限、网络同步合规性）。
   - **准则命名、目录结构与 scope 管理完全由项目实际开发者自行研究决定**，扩展不设强制约束。
2. **可执行工具链 (Project Tools / Scripts)**：
   - 维护方便 Agent 与开发者一键调用的取证脚本或命令（如无头测试运行器、Gym 场景入口、性能采样与抓帧工具）。
   - 在项目的 `AGENTS.md` 或自动化脚本中说明明确的运行方式与参数来源。

### 3. 规划与执行流（to-plan 协作）

- **规划期**：`to-plan` 在规划游戏开发任务时，聚焦于业务需求与任务切分，无需关注抽象的插槽实体。依据项目 `AGENTS.md` 的指引，将项目自备的验收原则与一键取证命令自然注入对应 Task。
- **执行期**：`execute-task` 依据 Task 注入的具体命令在引擎或测试环境中运行并采集证据。
- **审核期**：`delivery-review` 依据注入的项目原则指标对交付物出具审计结论。

---

## 落地建议：渐进式取证（如无必要，勿增实体）

项目无需在初始阶段盲目建设全套重度基础设施，应根据项目阶段阶梯式演进：

1. **白盒原型期 (Tier 1)**：关注核心玩法循环验证。依赖基础无头断言日志与试玩录屏/截图，不强求帧分析或微秒级性能分析。
2. **功能演化期 (Tier 2)**：关注逻辑稳定性与多机制组合。引入自动化测试套件与最小 Test Gym 场景，提供快速复现能力。
3. **性能与发布期 (Tier 3)**：关注多机型适配与渲染负载。部署自动化性能采样、DrawCall/Overdraw 监控与帧抓取工具，严格对照性能预算验收。

---

## 项目接入与迁移

新项目接入流程、游戏设计文稿（`docs/gameplays/`、`docs/GAME-VISUALS.md`）路径规范与存量迁移要求，请查阅 [game 扩展接入说明](skills/extension-setup-game/SKILL.md)。
