---
description: 区分数据结构与状态对象、在数据领域内分离状态承载与行为逻辑时使用。
---
# Separate Passive Data from Stateful Objects

- **Goal:** Give every type a clear role and decouple state storage from complex domain behavior.
- **Procedure:**
  1. Data types (domain state records, messages, configuration, snapshots, DTOs) expose their fields, represent pure state without business behavior, and prefer immutability.
  2. Within a data domain, separate state carriers from complex behavior: put domain rules, cross-entity calculations, and state transitions in stateless functions or services operating on data types, rather than accumulating them into bloated entity classes.
  3. When encapsulating a local invariant in a stateful object, hide its mutable fields and restrict methods to the minimal operations that maintain that invariant.
  4. Never mix exposed mutable fields with business methods on one type; split it into state data and a behavior module, or hide its fields behind invariant-preserving operations.
- **Exceptions:** Define framework-required entity types (ORM entities, engine components) according to framework conventions, and put business rules elsewhere.
