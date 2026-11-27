---
description: 多处按同一标签分支时，判断哪些分支实现了同一条规则并应共同维护。
---
# Centralize Repeated Dispatch for the Same Rule

Identify the question each branch answers. Consolidate branches when changing a variant's handling for one rule requires the same edit at every site. Keep independent decisions with their owners. An order's status can determine both its display color and its refund eligibility, and either mapping can change independently.

At the owner, use an exhaustive match or a lookup table for a fixed mapping, a strategy for interchangeable behavior, or a state machine for transition rules. Use exhaustiveness checking where available. Translate external tags into internal values at the integration boundary when their meanings differ.
