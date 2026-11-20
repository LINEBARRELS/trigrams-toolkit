# Python 强可转化原则（static）

下列 principle 的核心条款可直接转化为 Pyright / mypy、Ruff 与模块依赖检查工具的确定性检查。实际配置前，通过 `handbook load` 读取对应正文核对例外条件。

## `core:principle:programming-scale/keep-code-within-scale-limits`

- **验证工具**：Ruff（Pylint / McCabe 指标规则族）+ 轻量 CI 物理行数检查（按需）。
- **映射方向**：
  - 声明参数上限 → 参数数量上限规则（不计绑定接收者 `self`／`cls`）。
  - 函数有效行上限与控制流嵌套深度上限 → 函数语句数／复杂度／嵌套分支上限规则。
  - 手写源文件物理行上限 → 排除生成代码与快照夹具后由轻量脚本或等效规则检查。
- **档位参数**：按用户选定档位填入 `personal` / `small` / `medium`（默认）/ `large` 对应数值。

## `core:principle:programming-python/distinguish-python-none-and-manage-context-exceptions`

- **验证工具**：Ruff。
- **映射方向**：
  - `None` 显式身份比较 → 拦截 `== None`／`!= None`，强制使用 `is None`／`is not None`。
  - 上下文资源管理 → 拦截未使用 `with` 管理文件等上下文资源的写法。
  - 异常捕获与转换链 → 拦截裸 `except:`、过宽的盲目异常吞没以及 `except` 块内转换异常时遗漏 `raise ... from err`。
- **注意**：`if value` 与 `if value is None` 在业务上是否允许把空集合或零值当作假值，仍需在 Review 中核对语义。

## `core:principle:programming-python/declare-safe-python-signatures-and-module-exports`

- **验证工具**：Ruff + Pyright / mypy。
- **映射方向**：
  - 禁止可变默认参数 → 启用可变函数参数默认值检测规则。
  - 包公开导出与私有边界 → 校验 `__init__.py` 的 `__all__` 导出定义，拦截跨模块访问单下划线 `_` 私有成员。
- **注意**：公开函数滥用 `**kwargs` 隐藏实际参数以及项目统一基异常的语义设计，仍应在 Review 中把关。

## `core:principle:programming-design-module/keep-module-dependencies-acyclic`

- **验证工具**：`import-linter` 或 `tach`。
- **映射方向**：
  - 声明模块／子包边界并启用无环依赖检查，阻断跨模块循环 `import`（允许单模块内部互引用）。

## `core:principle:programming-design-architecture/point-dependencies-inward-toward-business-decisions`

- **验证工具**：`import-linter`（分层契约）或 `tach`。
- **映射方向**：
  - 识别领域决策层、编排层与外部交互层对应的 Python 包路径。
  - 禁止领域层包导入 Web 框架、UI、ORM、存储、网络与具体第三方 SDK，仅允许依赖标准库与内层领域类型。

## `core:principle:programming-design-repo/name-shared-code-by-domain-knowledge`

- **验证工具**：`tach` 或轻量化 CI 路径检查脚本。
- **映射方向**：
  - 拦截新增的 `utils.py`、`helpers.py`、`common.py`、`misc.py` 或同名杂物间子包。
  - 存量项目已有历史杂物间路径时，将其加入豁免列表冻结，仅阻止继续新增。
