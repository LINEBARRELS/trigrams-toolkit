---
description: 划分表现渲染、外部交互、编排逻辑与业务数据决策职责边界时使用。
---
# Separate Business Decisions from External Details

- **Goal:** Keep domain data and business decisions independent of rendering, UI, storage, networking, and frameworks.
- **Procedure:**
  1. Classify each piece of logic in the current design into one of three categories: business decisions (domain data, rules, calculations, state transitions), orchestration (invoking decision logic and external capabilities in sequence), or external interactions (rendering, UI, framework callbacks, I/O, third-party services).
  2. Separate rendering and presentation from domain data: business decision logic accepts domain data and returns results without holding presentation state or invoking external interaction code.
  3. Orchestration retrieves data, invokes decision logic, and passes results to storage or presentation. It contains no business decisions of its own.
  4. If a function or type contains logic from two or more categories, split it by category.
- **Exceptions:** Scripts and one-off tools may omit layers when their logic is only a few dozen lines and its parts do not change independently.
