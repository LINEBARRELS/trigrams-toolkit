---
name: 游戏程序开发
description: 消费正式玩法规则，沿用架构到装填两阶段流程，按需组织规则装填、视听表现装配、调试支撑与渲染验证，交付可运行成果与运行证据。
resourceId: game:workbook:game-programming-development
includes:
- game:principle:gameplay-rules/derive-acceptance-from-owned-gameplay-rules
- game:principle:runtime-evidence/bind-runtime-evidence-to-version-and-environment
- game:principle:runtime-evidence/make-gameplay-validation-scenarios-reproducible
- game:principle:runtime-evidence/choose-evidence-that-can-support-the-claim
- game:principle:runtime-evidence/bound-conclusions-to-verified-acceptance
---

# 游戏程序开发

## 适用与输入

取得本次开发相关的正式 Gameplay Spec。没有具体的玩法 Spec 则停止工作，请求指派明确的正式玩法 Spec。

核心架构与装填范式遵循 `core:workbook:programming-development`。本方法针对游戏领域的实时状态机、视听反馈、交互调试与渲染特性，补充专精的工作流与交接约定。

## 必要工作流程

1. **识别规则与反馈切片**：阅读 Gameplay Spec，梳理本次负责装填的实体状态、规则结算（`R-xx`）与互动反馈（`F-xx`）。按需运行 `handbook list --kind principle --scope gameplay-rules`，加载合法状态、约束一致性与转移判定原则。
2. **架构定义与 Stub 安装（架构阶段）**：确立模块分层，安装系统接口、数据结构/组件、状态机骨架与事件契约（Stub），并于交接要求中指明本次待装填的 `R-xx` 与 `F-xx` 范围。
3. **按需装填与调试验证（装填阶段）**：
   - **规则装填**：优先实现纯规则逻辑与状态流转，通过无头（Headless）运行或自动化测试覆盖 `R-xx` 与状态不变式，保障逻辑确定性。
   - **表现装配（按需）**：监听逻辑事件，装配动画、特效、音效与 HUD 动效，验证 `F-xx` 出现时机与操作反馈。
   - **调试支撑（按需）**：面对长流程或复杂边界条件时，提供轻量调试入口（如独立 Test Gym 场景、作弊控制台指令或状态可视化 Gizmo），便于秒级复现目标状态。
   - **渲染专项（按需）**：涉及自定义 Shader、材质管线或性能敏感模块时，采集 DrawCall、Overdraw 或 GPU 耗时证据。
4. **运行证据与对照验收**：
   - 使用 Godot 时读取[引擎配套方法](references/godot.md)，明确运行入口、启动参数与场景路径；
   - 采集无头断言日志、试玩录屏、操作截图或性能指标，逐项对照 Spec 中的 `R-xx` 与 `F-xx` 验收断言；
   - 涉及帧率、内存或计算负载性能验收时，加载 `game:principle:runtime-evidence/judge-performance-against-established-budgets`；
   - 运行材料改动时，加载 `game:principle:runtime-evidence/reassess-evidence-when-runtime-materials-change`。

## 工序切分与交接

坚持“先架构后细节”的两阶段交接，并在规划期将各功能单元的 Stub 边界与多阶段审核要求直接写入 Plan 正文。每个功能开发单元以架构阶段起步，安装并审核 Stub 框架；装填阶段专注于具体实现与调试验证。根据玩法特性复杂度与关注点分离需求，装填阶段按需分流，不强制每个 Plan 均包含全部类型：

| 工序职责与分流 | 适用场景与关注重点 | 对应 Spec 依据 | 下游交付物与必备证据 |
| --- | --- | --- | --- |
| **架构安装**（必选） | 确立模块层级、安装数据结构、主循环骨架与事件契约 | Spec 架构与实体定义 | Stub 框架代码、签名与安装验证，为后续装填锁定接口与边界 |
| **规则装填**（必选） | 装填纯规则逻辑、数值计算、状态转移与边界不变式，保障逻辑确定性并解耦表现 | `R-xx` 规则编号 | 核心逻辑代码、无头（Headless）测试日志与状态断言；作为逻辑回归基线及联机/存档一致性保障 |
| **表现装配**（按需） | 监听规则事件，装配动画融合、特效、音效与 HUD，关注操作反馈时机与手感 | `F-xx` 反馈编号 | 视听预制体/场景连线、操作反馈录屏与对照图；确认资源挂载无遗漏且表现无迟滞 |
| **调试支撑**（按需） | 面对复杂边界状态、长流程玩法或高成本复现场景，关注秒级直达与环境隔离 | 目标极限状态验证 | 最小 Test Gym 场景、作弊快捷指令与操作说明；供后续长流程工作快速复现及自动化测试复用 |
| **渲染专项**（按需） | 自定义 Shader、材质管线、大场景合批或超预算调优，关注管线负载与合批表现 | 渲染预算与视觉标准 | Shader 代码、材质配置、抓帧分析或性能对比表；对照项目性能预算裁决，防范渲染性能劣化 |

### 与 Gameplay Spec 强绑定规范

- **正式依据关联**：规划涉及玩法实现的 Plan 时，明确声明关联的 Gameplay Spec Artifact ID。
- **正文条目锚定**：在对应 Stub 的范围与验收标准中，明确标出本次负责实现的具体 `R-xx` 规则号与 `F-xx` 反馈号。
- **交付逐项对照**：交付结果文档应对所领取的 `R-xx` 与 `F-xx` 逐项给出直接验证证据，未验证项单独列明原因。

## 产出与验收

1. **安装验收**：架构阶段交付的框架代码与公共契约一致，Stub 标注清晰，项目编译或类型检查通过。
2. **规则验收**：无头环境运行断言测试，确认覆盖全部约定的 `R-xx` 规则、不变式及边界情况。
3. **表现验收**：在实际图形环境中运行，录屏或截图证实 `F-xx` 交互反馈出现的时机、手感与显示符合预期。
4. **调试与专项验收**：若包含调试支撑或渲染专项，验证 Gym 场景可秒级加载、作弊指令有效、渲染指标在预算范围之内。
