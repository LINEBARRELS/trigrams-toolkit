# 工具包维护与发布

本文件维护 Trigrams toolkit 源码仓库的开发、校验与发布说明。体系设计与分发层次见[架构说明](../skills/toolkit-steward/references/architecture.md)，开发环境准备与项目接入见[开发与接入](getting-started.md)。

## 唯一维护源

下列路径相对工具包仓库根：

| 组件 | 维护位置 | 说明 |
| --- | --- | --- |
| 通用 Skill 与资料 | `skills/` | 保留 Skill 名称；workbook、principle 随各自 Skill 维护 |
| 扩展 Skill | `extensions/<extension>/skills/` | setup 的 `assets/extension.json`、`principles/`、`workbooks/` 携带资源 |
| 公共工具 | `src/trigrams_toolkit/` | 项目上下文、Registry、Plan、资料与安装服务 |
| 核心类型 | `src/trigrams_toolkit/resources/state/core-types.json` | 唯一类型声明；通过包资源读取 |
| 适配器 | `src/trigrams_toolkit/resources/adapters/` | Codex、Claude 与 Pi Web 模板，随 CLI 包交付 |
| 源码索引 | `toolkit.json`、`skills/resources.json` | 供仓库校验（`scripts/verify_toolkit.py`）定位源码资料；安装后由已安装 Skill 与项目快照独立发现 |

修改维护源时，同步更新实际调用方、契约与说明。workbook、principle 的身份、头信息和加载语义见[架构说明](../skills/toolkit-steward/references/architecture.md)。历史 Plan、Task 与交付证据保留原样。

## 验证

Python 源码需 3.11+，通过 `python -m pip install -e '.[dev]'` 安装可编辑包、运行依赖和开发检查工具。依赖与四个标准命令在 `pyproject.toml` 单点声明。

```sh
python tasks.py check
```

底层分别调用 `scripts/verify_toolkit.py`、`scripts/check_protocols.py` 与 `python -m mypy`。前两个脚本只读校验源码资料、Skill 元数据、适配入口、schema 引用闭包与命令声明。资料正文变动无需生成或同步包声明。

| 改动范围 | 验证方式 |
| --- | --- |
| Skill、资料、适配器和说明 | `python tasks.py check` 及实际加载；纯文字改动无需新增代码测试 |
| Plan 与 handbook | `tests/runtime/` 中相关行为测试 |
| 安装、归档与源码校验 | `tests/` 中相关定向测试 |
| 多工具协作 | `tests/test_source_acceptance.py`。从临时项目根调用当前源码，覆盖资料、Registry、Plan 与安装归属 |
| Project State | `tests/test_project_state.py` 与 `tests/test_project_paths.py`；覆盖身份、文稿保真、锁与平台路径 |
| 打包与发布 | `python tasks.py build` 输出至 `dist/`，随后运行 `python tasks.py verify-package` 隔离验收，确认后执行 `python tasks.py publish` |

过程回执放在 `.tmp/`。记录平台、Python 版本、已运行的命令与未验证范围。源包与安装包验收使用隔离的 Skill 目录和临时项目，覆盖快照装配、全局依赖补齐与旧记录迁移。包验收隔离 uv 工具目录、bin、缓存及宿主 `PYTHONPATH`。从项目外检查帮助与版本，在隔离项目根验证标准入口和 Bash／pwsh 参数传递。

## CI 与发布

`.github/workflows/ci.yml` 使用只读权限，在 Ubuntu 与 Windows 的 Python 3.11／3.13 矩阵上分两档执行检查：

- **PR 检查**：运行 `mypy`、`scripts/verify_toolkit.py`、`scripts/check_protocols.py` 及 `tests/`、`tests/runtime/` 测试。
- **发布候选与定时验收**：在版本标签（`v*`）、手动触发（`workflow_dispatch`）或每日定时检查（有近期提交时）运行上述全部检查，并额外构建直接 wheel、sdist 与由 sdist 生成的 wheel，使用合成项目与隔离 Skill 目录执行 `scripts/check_package.py` 跨平台隔离安装验收；详细原始回执留在 `.tmp/`。

发布新版本时，对齐 `toolkit.json`、`pyproject.toml` 与随包发布的 core 及扩展清单中的 `version`（`schemaVersion`、`protocolVersion` 与运行状态 revision 各自按协议维护），更新 `CHANGELOG.md`，通过源码校验、测试与隔离包验收并核对 sdist／wheel 文件清单与随包许可后，推送 GitHub 标签并上传对应发行包到 PyPI。
