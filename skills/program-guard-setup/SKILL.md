---
name: program-guard-setup
description: 根据项目编程语言与既有工具链现状，将可机械化校验的编程 principle 转化为编译器、Linter 与架构依赖检查配置，用于项目初始化装配或开发纠错后的增量规则沉淀。
disable-model-invocation: true
metadata:
  harness-toolkit-type: workflow
---

# program-guard-setup

根据项目编程语言与工程现状，将适用的编程 principle 落实为编译器、Linter 与架构依赖检查配置。支持项目初始化装配与后续增量补齐。

## 必要工作流程

1. **探测项目现状**：检查目标仓库的编程语言、运行时与工具版本、已有编译器／Linter／架构检查配置及 CI 入口，区分全新项目与存量项目。同时检查 `DEVTECH.md`（“应用架构”）与 `docs/ARD.md`，确认是否已确立架构层、工程载体、允许依赖方向、组合根与模块边界。已有主流工具链时优先复用。
2. **加载语言参考与原则清单**：
   - 按目标语言读取对应参考目录：
     - TypeScript / JavaScript：[toolchain.md](references/typescript/toolchain.md)（必读）、[static.md](references/typescript/static.md)（强可转化映射）与 [partial.md](references/typescript/partial.md)（半可转化映射，按需读取）。
     - C# / .NET：[toolchain.md](references/csharp/toolchain.md)（必读）、[static.md](references/csharp/static.md)（强可转化映射）与 [partial.md](references/csharp/partial.md)（半可转化映射，按需读取）。
     - Python：[toolchain.md](references/python/toolchain.md)（必读）、[static.md](references/python/static.md)（强可转化映射）与 [partial.md](references/python/partial.md)（半可转化映射，按需读取）。
   - 使用 principles skill 加载并阅读选中的内置 principle 正文，核对每条原则的适用条件与例外。
      - 若存在现场发现的可机械化校验的条款，纳入本次候选。
   - 未列入 `static.md` 与 `partial.md` 的内置原则归入语义审查层，不强行编造静态规则。
3. **对齐范围与存量策略**：向用户说明拟搭建的验证工具链、本次落地的 principle 范围、规模上限档位（默认 `medium`）以及存量代码启用策略。`DEVTECH.md` 与 `docs/ARD.md` 已确立应用架构时，优先依据设计文档配置全局架构与依赖边界检查，不从存量代码反推分层。架构层与模块边界尚未定稿时，先配置语言门禁与通用检查，待架构定稿后再增量补齐。用户已明确指定时直接执行。
4. **版本核验与增量装配**：
   - 以目标项目实际安装的工具版本与 `toolchain.md` 中的官方文档为准核验接入方式、配置格式、规则名称与校验命令，不凭记忆写入未核验的规则 ID。
   - 增量合并或生成配置文件，并在每组规则上方标注来源注释（格式：`from <principleId>`，涉及具体架构边界时附注文档章节），便于后续追溯与维护。
   - 仅将 `partial.md` 中可确定性拦截的子条款写入配置，剩余语义条款记入交付清单留给 Review。
5. **实跑验证与交付**：
   - 实际运行编译器、Linter 与架构依赖检查命令，确认配置语法合法、规则生效且不破坏既有构建。
   - 交付三项内容：已落地的 `principleId` 与架构契约到配置规则的映射表、留给 Review 或待架构定稿后补齐的清单、以及实跑命令输出（存量项目附带现有违例概览与收敛建议）。

## 存量项目渐进策略

在已有大量历史代码的仓库中启用新门禁时，不应一次性以 `error` 阻断全仓提交。按项目阶段选用下列策略之一：

- **分层严格**：核心领域目录与新增模块启用 `error`，历史目录暂设 `warn` 并记录收敛计划。
- **增量门禁**：在 CI 中对变更文件运行严格检查，全仓保持既有基线。
- **单点豁免**：确需豁免的合法特例（如协议固定签名或内聚算法）使用行级豁免注释并写明理由，不在文件头或全局关闭规则。
