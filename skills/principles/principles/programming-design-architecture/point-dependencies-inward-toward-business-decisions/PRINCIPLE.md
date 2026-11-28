---
description: 设计架构层依赖方向、划分核心领域与基础设施边界或定义依赖接口时使用。
---
# Point Dependencies Inward Toward Business Decisions

- **Goal:** Change external I/O details without modifying core domain decisions.
- **Procedure:**
  1. Direct dependencies inward: entry adapters → orchestration → core domain; external infrastructure (storage, network, SDKs) implements inner-layer interfaces and wires at the composition root.
  2. Keep core domain modules free of external dependencies. Declare required interfaces on the orchestration side using domain terms and types, hiding third-party types.
  3. Remove UI, persistence, network, or infrastructure imports from domain and orchestration modules.
- **Exceptions:** Standard libraries, pure primitives, and non-replaceable base types (e.g., engine math types).
