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
| 打包与发布 | `python tasks.py check-release --tag vX.Y.Z` 核对版本一致，`python tasks.py build` 输出至 `dist/`，`python tasks.py verify-package` 隔离验收；正式发布由 `v*` 标签触发 `.github/workflows/release.yml` 自动上传 PyPI |

过程回执放在 `.tmp/`。记录平台、Python 版本、已运行的命令与未验证范围。源包与安装包验收使用隔离的 Skill 目录和临时项目，覆盖快照装配、全局依赖补齐与旧记录迁移。包验收隔离 uv 工具目录、bin、缓存及宿主 `PYTHONPATH`。从项目外检查帮助与版本，在隔离项目根验证标准入口和 Bash／pwsh 参数传递。

## CI 与发布

仓库拆分日常校验与标签发布两条工作流，隔离只读检查与发布凭据。

### 日常与候选校验（`.github/workflows/ci.yml`）

`.github/workflows/ci.yml` 全程使用 `contents: read` 只读权限，在 Ubuntu 与 Windows 的 Python 3.11／3.13 矩阵上分两档运行：

- **PR 检查**：运行 `mypy`、`scripts/verify_toolkit.py`、`scripts/check_protocols.py` 及 `tests/`、`tests/runtime/` 测试。
- **候选与定时验收**：手动触发（`workflow_dispatch`）或每日定时检查（过去 24 小时有提交时）运行全部静态检查与测试，并构建直接 wheel、sdist 与由 sdist 生成的 wheel，在合成项目与隔离 Skill 目录中运行 `scripts/check_package.py` 跨平台验收。

### 标签自动发布（`.github/workflows/release.yml`）

推送 `v*` 标签后，`.github/workflows/release.yml` 自动完成构建、验收与 PyPI 发布，本机无需保存 PyPI API Token：

1. **`build` 作业**：在 `ubuntu-latest` 上运行 `python tasks.py check-release --tag <tag>` 核对版本与 `CHANGELOG.md`，运行 `python tasks.py check`，再运行 `python tasks.py build` 单次构建 sdist、wheel 与校验用直接 wheel。
2. **`verify` 作业**：在 Ubuntu 与 Windows 的 Python 3.11／3.13 矩阵上下载 `build` 产出的同一批包，运行 `tasks.py check`、`tasks.py test` 与 `tasks.py verify-package`。
3. **`publish-pypi` 作业**：仅在 `build` 与全部 `verify` 矩阵通过后运行；该作业绑定 GitHub Environment `pypi`，仅申请 `id-token: write` 权限，通过 `pypa/gh-action-pypi-publish` 使用 OIDC Trusted Publishing 上传已验收的 `dist/` 发行包并附带 PEP 740 数字证明。

#### 首次启用 Trusted Publishing 配置

在 PyPI 项目设置（`https://pypi.org/manage/project/trigrams-toolkit/settings/publishing/`）中登记 GitHub Publisher：

| 字段 | 值 |
| --- | --- |
| Owner | `LINEBARRELS` |
| Repository name | `trigrams-toolkit` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

同时应在 GitHub 仓库的 `Settings -> Environments` 中创建同名环境 `pypi`，并将部署规则限制为仅允许 `v*` 标签（可选开启人工审批）。

#### 发布新版本步骤

**警告：** 不要推送尚未对齐版本号的 `v*` 标签。`build` 作业会在版本或 `CHANGELOG.md` 不匹配时中止发布。

1. 对齐 `pyproject.toml`、`toolkit.json`、`skills/resources.json` 与各扩展 `extension.json` 中的 `version`（`schemaVersion`、`protocolVersion` 与运行状态 revision 按协议独立维护）。
2. 在 `CHANGELOG.md` 中新增对应 `## <version>` 节。
3. 运行本地核对：`python tasks.py check-release --tag v<version>` 与 `python tasks.py check`。
4. 提交变更并推送到 `main`，再创建并推送附注标签：
   ```sh
   git tag -a v<version> -m "Release v<version>"
   git push origin v<version>
   ```
   结果：GitHub Actions 自动运行 `Release to PyPI`，全部跨平台验收通过后发布至 PyPI。

如需本地试发 TestPyPI 或应急手动上传，可使用 `python tasks.py publish --test`（或 `--dry-run` 预演）。
