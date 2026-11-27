---
description: 划分模块或评估需求变更影响面时，判断哪些职责应共同维护。
---
# Group Module Responsibilities by Reason to Change

Trace a few plausible requirement changes through the proposed modules. Stakeholders can help identify these changes. For each one, identify the rule, format, or protocol that would change and the code that owns it.

- Keep a rule's constants, validation, and calculations together when they must change in step. If several modules encode the same decision, give it one owner and have its consumers use that contract.
- Separate responsibilities that can change independently. A refund policy and its presentation can evolve separately even when the same team owns both.
- A feature can require coordinated changes across several contracts. Keep each contract with its owner. For a shared protocol, a single definition can keep consumers consistent across modules.
