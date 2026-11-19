---
description: 编写自定义代码或新增抽象前按极简阶梯逐级排查现成方案时使用（pragmatic.simplicity-ladder）。
---
# Evaluate Solutions Along the Simplicity Ladder

- **Goal:** Prevent over-engineering by exhausting simpler and existing options before authoring custom logic or adding abstractions.
- **Procedure:**
  1. Evaluate candidate solutions against the simplicity ladder in strict top-to-bottom order. Stop at the first rung that satisfies the requirement:
     - **Rung 1 (YAGNI):** Question the requirement. Can the problem be solved without adding new code (e.g. deleting dead code, adjusting existing configuration, or challenging speculative features)?
     - **Rung 2 (Repository Reuse):** Search the repository for existing helpers, utilities, domain types, or components that already implement or closely match the needed behavior.
     - **Rung 3 (Standard Library & Platform):** Use native language features, standard library modules, or runtime/platform capabilities (e.g. built-in string/collection utilities, native Web APIs) before creating custom helpers.
     - **Rung 4 (Installed Dependencies):** Check already installed project packages. If a dependency is already in the project manifest and fits the responsibility, use it instead of writing custom alternatives. Do not add a new dependency for minor logic.
     - **Rung 5 (Single Expression / Inlining):** If an operation is obvious, readable, and self-contained, express it inline or in a single concise line rather than introducing dedicated helper methods, classes, or multi-file plumbing.
     - **Rung 6 (Smallest Complete Change):** When custom code is truly necessary, write only the minimal, cohesive delta required to fulfill the task.
  2. Do not introduce speculative extension points, multi-tiered wrapper layers, or factory patterns for single-use scenarios.
- **Exceptions:** Public API surface requirements and framework-mandated boilerplate (such as required lifecycle hooks or interface implementations).
