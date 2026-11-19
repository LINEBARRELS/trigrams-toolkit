---
description: 在 TypeScript／JavaScript 中编排 Promise 并发、处理共享状态浅拷贝或使用空值合并时使用。
---
# 管控 JavaScript Promise 并发并防范浅拷贝与假值陷阱

编写 TypeScript／JavaScript 异步操作、状态拷贝与缺省回退逻辑时，应防范浮动 Promise、浅层引用别名与假值误判：

- **Promise 生命周期与并发：** Promise 应被返回、`await` 等待或交由明确的后台生命周期管理；需等待回调完成时禁用 `forEach(async ...)`；批量并发时应控制并发数以匹配外部容量。
- **共享状态与浅拷贝：** `const` 和 `readonly` 不保证深层不可变；注意闭包变量捕获、对象引用别名，以及对象／数组展开语法（`{ ...obj }`）仅执行浅拷贝。
- **缺失值与回退：** 严格区分 `null`、`undefined` 与有效的 `0`、空字符串 `""`、`false`；缺省回退按业务语义选择空值合并 `??`（仅过滤 `null`／`undefined`）或逻辑或 `||`。
