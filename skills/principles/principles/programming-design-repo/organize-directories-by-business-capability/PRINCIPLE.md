---
description: 组织顶层目录结构与特性子目录划分时使用。
---
# Organize Directories by Business Capability

- **Goal:** Make the directory structure reveal what the system does.
- **Procedure:**
  1. Organize top-level directories by business capability or feature (`Combat/`, `Inventory/`, `Billing/`), not by technical category (`Controllers/`, `Models/`, `Services/`).
  2. Place technical layers inside feature directories. Small features may not need subdirectories.
  3. Implementations of external interactions (storage, networking, platform adapters) may be grouped in a separate directory. Define the required capabilities on the business side and implement them in the external interaction directory.
  4. Keep entry points and composition code in a separate location.
- **Exceptions:** Follow framework-mandated directory conventions, such as Unity's `Editor/` or Next.js's `app/`.
