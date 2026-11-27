---
description: 组织应用入口依赖装配与配置注入时使用。
---
# Wire Dependencies at the Composition Root

- **Goal:** Make dependency wiring visible in one place and keep business code independent of object creation.
- **Procedure:**
  1. Create implementations of external interactions centrally at the application entry point (`Main`, a startup scene, or an application factory), and inject them into their consumers.
  2. Business and orchestration code receive dependencies through constructor or function parameters. They neither instantiate implementations of external interactions internally nor retrieve dependencies through a service locator.
  3. Read configuration values at the entry point, convert them to explicit types, and pass them to lower layers.
- **Exceptions:** Framework-defined creation mechanisms (DI containers, engine components) may replace a handwritten entry point, but the composition rules should still be centralized.
