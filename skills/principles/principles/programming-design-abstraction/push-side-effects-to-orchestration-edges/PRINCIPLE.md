---
description: 分离纯规则计算与文件、网络、状态修改等副作用时使用（abstraction.effect-edge）。
---
# Push Side Effects to Orchestration Edges

- **Goal:** Make most logic understandable and testable from its inputs and outputs alone.
- **Procedure:**
  1. Express rule calculations as functions that accept data and return results without reading or writing external state.
  2. Concentrate side effects (writing files, sending requests, modifying shared state, publishing events) in orchestration and external interaction code.
  3. A function should either modify state or return information. When it genuinely needs to do both, such as dequeuing an item, make the side effect explicit in its name.
  4. Do not use output parameters to return results.
- **Exceptions:** Language-idiomatic Try patterns, such as the `out` parameter in C# `TryParse`, may be retained.
