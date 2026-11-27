---
description: 为带约束的原始值、成组参数或状态类别声明领域类型与常量时使用。
---
# Model Domain Concepts with Explicit Types

- **Goal:** Give domain concepts explicit names and types, and validate their rules in one place.
- **Procedure:**
  1. Inspect primitive values with domain meaning: IDs, monetary amounts, coordinates, durations, percentages, and status codes. When a value has constraints, units, or format rules, define a dedicated type and validate it at construction.
  2. Define a single type for a group of values that always occur together (start and end times, position and orientation), or for two values with constraints relating them to each other.
  3. Represent states and categories with enums or union types, not string or integer literals.
  4. Declare values with business meaning (limits, multipliers, timeouts) as named constants in the module that owns the rule.
  5. Do not create parameter objects that group unrelated values merely to shorten a parameter list.
- **Exceptions:** Primitive values at serialization boundaries; performance-sensitive inner loops may use primitive values after type conversion at the enclosing boundary.
