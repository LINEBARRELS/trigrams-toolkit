---
description: 引入接口、基类、泛型参数或扩展点时，判断它在当前设计中承担什么职责。
---
# Require a Concrete Reason for Abstraction

Introduce an abstraction when at least one current responsibility justifies it:

- Support real variants that already need the same contract.
- Isolate an external dependency that needs to be replaceable.
- Enforce an invariant that callers would otherwise have to maintain.
- Hide complexity or a required sequence of operations from callers.

A published API or an extension point used by external plugins already has consumers whose contracts must be honored. When the proposed layer would only forward calls and has no responsibility of its own, keep the implementation concrete.
