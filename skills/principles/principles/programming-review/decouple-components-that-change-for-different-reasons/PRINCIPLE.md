---
description: 审查代码结构，排查反向依赖、内部实现泄漏、浅模块与调用方特判污染等不必要耦合时使用。
---
# Decouple Components That Change for Different Reasons

- **Goal:** Reject structures that tie together components that change for different reasons or at different rates.
- **Procedure:**
  1. Verify dependency direction: reject stable domain or policy contracts that import volatile infrastructure, UI, or concrete external vendor types.
  2. Reject shallow modules and leaky signatures that expose internal storage layout, intermediate traversal chains, or raw implementation types to callers.
  3. Reject caller-vocabulary pollution: a general module or signature must not accept parameters, flags, or special-case branches (`if caller == X`) that only one specific caller workflow understands.
  4. When special cases or workaround flags appear in a contract, require redesigning the underlying boundary from first principles rather than stacking conditional patches.
- **Exceptions:** Composition roots and boundary adapters whose sole responsibility is wiring or translating between specific layers.
