---
description: 定义公开操作的失败返回语义、异常分类与边界输入校验时使用（abstraction.error-contract）。
---
# Define Explicit Error Contracts at Boundaries

- **Goal:** Let callers determine how an operation can fail from its signature and handle failure accordingly.
- **Procedure:**
  1. Define failure semantics for every public operation. Represent expected failures (not found, validation failure) through return values, using nullable types, result types, or the Try pattern. Throw exceptions for precondition violations or situations in which execution cannot continue.
  2. Use the same representation for the same category of failure within a module.
  3. Validate external input at the boundary and convert it into internal types. Do not repeat that validation in internal code.
  4. Define exception types according to how callers handle them: failures handled in the same way share a type; failures requiring different handling use different types.
  5. Fail immediately on impossible states instead of masking them with default values.
