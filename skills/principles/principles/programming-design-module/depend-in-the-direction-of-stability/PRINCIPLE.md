---
description: 规划高频变化模块与稳定基础模块之间的依赖方向时使用（module.stable-direction）。
---
# Depend in the Direction of Stability

- **Goal:** Avoid making many modules depend on frequently changing modules.
- **Procedure:**
  1. Assess each module's stability: the more dependents it has and the fewer dependencies it has, the more stable it is.
  2. Dependencies should point from volatile modules toward stable modules.
  3. Keep widely depended-on modules limited to type definitions, interfaces, and rules that remain unchanged over time. Put volatile concrete implementations in modules that depend on them.
  4. When a stable module needs to call a volatile module, invert the dependency through an interface as described in `layer.inward-dependency`.
