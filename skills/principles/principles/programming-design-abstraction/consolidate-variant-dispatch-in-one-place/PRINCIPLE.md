---
description: 处理跨多处出现的枚举、状态或类型标签分支时使用（abstraction.single-dispatch）。
---
# Consolidate Variant Dispatch in One Place

- **Goal:** Require changes in only one place when adding a variant.
- **Procedure:**
  1. List every location in the design that branches on the same type tag (an enum, state, or kind field).
  2. If there is only one location, use an exhaustive `switch` or pattern match.
  3. If there are two or more locations, consolidate the branching using one of these forms:
     - Use polymorphism or strategy objects when variants have different behavior.
     - Use a lookup table when variants differ only in data.
     - Use a state machine when there are transition rules between variants.
  4. If the language supports exhaustiveness checking, enable it at the consolidated decision point.
- **Exceptions:** Map third-party enums outside your control once at the system boundary.
