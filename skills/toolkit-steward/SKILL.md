---
name: toolkit-steward
description: 仅在任务明确涉及 Trigrams toolkit 体系时使用。解答工具包架构与组件分工，推荐适用的 Skill、workbook 和公共工具，诊断项目与环境状态，并引导项目接入与扩展管理。
metadata:
  harness-toolkit-type: workflow
---

# toolkit-steward

负责 Trigrams toolkit 体系咨询、能力选型、环境诊断，以及项目接入与扩展管理分流。

1. **体系咨询、能力选型或状态诊断**：将问题与已知上下文交给 subagent，指示其读取[咨询工作指引](references/consultation.md)并按需查阅专题资料或检查当前项目状态；由子代理返回结论、依据位置与下一步建议，不回传整篇文档。当前环境不支持 subagent 时，由当前 Agent 按同一指引执行。
2. **项目接入或扩展管理**：直接读取[项目接入与扩展管理](references/project-integration.md)，按项目现状执行首次接入、状态重建或扩展增补、同步与移除。工具或全局依赖异常时查阅[全局安装指引](references/deployment.md)。
