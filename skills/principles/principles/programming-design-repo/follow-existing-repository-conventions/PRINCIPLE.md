---
description: 新增目录、模块或接口前对齐仓库既有结构与复用现有能力时使用（repo.follow-existing）。
---
# Follow Existing Repository Conventions

- **Goal:** Keep new structure consistent with the existing repository and avoid duplicating existing capabilities.
- **Procedure:**
  1. Before designing, inspect the structure, naming, and layering of the affected directories, along with the public interfaces of related modules.
  2. Search the repository for types, functions, or modules with the same responsibility. When responsibilities match, reuse or extend the existing implementation instead of creating a parallel one.
  3. Follow existing conventions for directory organization, naming, and error handling.
