# 公共工具与项目接入

公共源码位于 `src/trigrams_toolkit/`。四个公共命令为 plan-toolkit、project-state、handbook、harness-install，由同一 Python 包的标准 console script 提供。

## 分发与运行边界

`uv tool install` 安装 CLI，Vercel skills 安装 Skill。包内 `resources/` 是 schema、命令声明、核心类型与 adapter 的维护源，使用 `importlib.resources` 读取；程序版本取自安装包元数据。

core 资料随全局 Skill 发布，扩展资料随项目 setup Skill 发布。Project State、Plan 与安装事务各自维护业务文件锁。`harness-install` 在应用装配时按需补齐目标 agent 的全局 Skill。

## 开发依赖

Python 最低版本为 3.11，运行与开发依赖在 `pyproject.toml` 单点维护。wheel 和 sdist 携带运行材料与许可；原则、workbook 和 Skill 正文继续使用 Skill 分发渠道。

## 公共解析与文件发布

`trigrams_toolkit.shared.serialization` 维护严格 JSON 解析。文档解析入口 `parse_json_document` 拒绝重复键、非整数数值（禁止浮点数与 NaN/Infinity 等常量）、无效 UTF-8 和语法错误，保留协议检查原有的任意精度整数及转义字符串输入。运行时 `parse_json` 在文档解析后核对安全整数范围与 Unicode scalar。`check_protocols` 的 Schema 文档和命令声明读取使用文档边界；现有 Plan、handbook 和安装运行时继续使用运行时边界。解析失败为 `ProtocolError(invalid_json)`；脚本在边界转换为自身错误，文件 I/O 异常由调用方处理。

`trigrams_toolkit.shared.files.atomic_write` 负责单文件原子发布、同目录临时文件、文件同步与临时文件清理。Windows 仅对文件占用的权限错误（WinError 5/32 的 PermissionError）作有限重试，持久失败保留异常。项目安装事务负责多文件操作及其回退。

## 项目根

四个公共 CLI 以进程当前目录的实际路径作为项目根。业务命令须在目标项目根执行，各 Git worktree 使用各自根目录。可从任意目录用 `-h` 或 `--help` 查看帮助，用 `-v` 或 `--version` 查看版本。Plan 的成果查询将同一个根交给 Project State 服务。

## 资料与安装

handbook 只发现 WORKBOOK.md 和 PRINCIPLE.md。workbook 头维护 name、description 及按需 resourceId、includes；includes 可递归包含 workbook 与 principle。principle 采用 principles/<scope>/<principle>/PRINCIPLE.md，名称、scope 和 ID 从包与目录派生，头信息只接受 description；单条加载只返回自身。list 每项只返回 resourceId、description；load 可批量读取入口，保留正文、来源、入口和 workbook 依赖。Package 声明来源、资料根、成果类型、关系和安装材料。Skill 由宿主发现。

`harness-install install preview` 预览项目快照变更，`harness-install install apply` 核对来源声明、路径归属及安装基线后应用。最近一次备份与回执保存在 `.harness/previous`，捕获写入错误后回退。`harness-install archive PATH...` 把明确选择的项目内相对路径原样移入当前项目的 `.harness-archive`，再使用当前工具重建。

Plan 与 Task 的状态只属于 plan-toolkit。Module、Feature 与正式成果身份属于 project-state。
