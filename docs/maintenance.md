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
| 源码索引 | `toolkit.json`、`skills/resources.json` | 供仓库校验（`scripts/verify_toolkit.py`）定位源码资料；安装后由已安装 Skill 与项目快照独立发现 |

修改维护源时，同步更新实际调用方、契约与说明。workbook、principle 的身份、头信息和加载语义见[架构说明](../skills/toolkit-steward/references/architecture.md)。历史 Plan、Task 与交付证据保留原样。

## 验证

Python 源码需 3.11+，通过 `python -m pip install -e '.[dev]'` 安装可编辑包、运行依赖和开发检查工具。依赖与四个标准命令在 `pyproject.toml` 单点声明。

```sh
python tasks.py check
```

底层分别调用 `scripts/verify_toolkit.py`、`scripts/check_protocols.py` 与 `python -m mypy`。前两个脚本只读校验源码资料、Skill 元数据、schema 引用闭包与命令声明。资料正文变动无需生成或同步包声明。

| 改动范围 | 验证方式 |
| --- | --- |
| Skill、资料和说明 | `python tasks.py check` 及实际加载；纯文字改动无需新增代码测试 |
| Plan 与 handbook | `tests/runtime/` 中相关行为测试 |
| 安装、归档与源码校验 | `tests/` 中相关定向测试 |
| 多工具协作 | `tests/test_source_acceptance.py`。从临时项目根调用当前源码，覆盖资料、Registry、Plan 与安装归属 |
| Project State | `tests/test_project_state.py` 与 `tests/test_project_paths.py`；覆盖身份、文稿保真、锁与平台路径 |
| 打包与发布 | `python tasks.py check-release --tag <tag>` 核对对应的版本和更新记录。CLI 包使用 `python tasks.py build` 构建，再用 `python tasks.py verify-package` 隔离验收。 |

过程回执放在 `.tmp/`。记录平台、Python 版本、已运行的命令与未验证范围。源包与安装包验收使用隔离的 Skill 目录和临时项目，覆盖快照装配、全局依赖补齐与旧记录迁移。包验收隔离 uv 工具目录、bin、缓存及宿主 `PYTHONPATH`。从项目外检查帮助与版本，在隔离项目根验证标准入口和 Bash／pwsh 参数传递。

## CI 与发布

仓库采用 `dev`（日常集成）+ `main`（正式发版）双分支策略，并拆分日常校验与标签发布两条工作流，隔离只读检查与发布凭据。分支职责与合并策略见[参与维护](../CONTRIBUTING.md#分支与合并模型)。

### 版本来源

| 发布对象 | 版本来源 | 更新记录 | Git 标签 |
| --- | --- | --- | --- |
| 工具包 Skill 与资源 | `toolkit.json`、core 资源清单和各扩展清单 | [工具包更新记录](../CHANGELOG.md) | `vX.Y.Z` |
| CLI 包及随包交付的协议与类型 | `pyproject.toml` 的 `[project].version` | [CLI 更新记录](cli-changelog.md) | `vcli-X.Y.Z` |

两个版本号各自递增。四个公共 CLI 的 `--version` 读取 CLI 包版本。数据协议和运行状态的版本字段由各自契约维护。

修订 Skill、workbook 或 principle 时，可单独发布工具包。依赖新 CLI 能力的 Skill 应在该 CLI 发布后再合入 `main`，因为默认 Skill 安装入口读取 `main`。历史标签沿用发布时的版本含义。

### 日常与候选校验（`.github/workflows/ci.yml`）

`.github/workflows/ci.yml` 使用 `contents: read` 权限，在 Ubuntu 与 Windows 的 Python 3.11／3.13 矩阵上运行以下检查。

- **日常 PR 检查（`base != main`）**：运行 `mypy`、`scripts/verify_toolkit.py`、`scripts/check_protocols.py` 及 `tests/`、`tests/runtime/` 测试。
- **发版 PR**核对工具包和 CLI 的版本声明及更新记录，并运行源码检查与测试。涉及 CLI 包内容、构建或验收流程时，再构建直接 wheel、sdist 与由 sdist 生成的 wheel，并跨平台隔离验收。
- **手动与定时检查**运行源码检查、测试和隔离包验收。定时检查在 `origin/dev` 过去 24 小时有提交时检出 `dev`。

`PR checks` 汇总 PR 的四组平台检查。四组均成功时，`PR checks` 才通过。

### CLI 自动发布（`.github/workflows/release.yml`）

推送 `vcli-X.Y.Z` 标签后，GitHub Actions 使用 PyPI Trusted Publishing 发布 CLI 包。

1. **`build` 作业**校验标签提交位于 `origin/main` 历史中，再核对标签、`pyproject.toml` 和 CLI 更新记录。`python tasks.py build` 构建 sdist、wheel 与校验用直接 wheel。
2. **`verify` 作业**在 Ubuntu 与 Windows 的 Python 3.11／3.13 矩阵上下载 `build` 产出的同一批包，并执行 `python tasks.py verify-package`。合并前的四组平台作业负责源码静态检查和源码测试。
3. **`publish-pypi` 作业**：仅在 `build` 与全部 `verify` 矩阵通过后运行；该作业绑定 GitHub Environment `pypi`，仅申请 `id-token: write` 权限，通过 `pypa/gh-action-pypi-publish` 使用 OIDC Trusted Publishing 上传已验收的 `dist/` 发行包并附带 PEP 740 数字证明。

#### 首次启用仓库保护与 Trusted Publishing

1. 在 GitHub 仓库 `Settings -> Rules -> Rulesets` 中建立两条规则：
   - **分支规则（`main`）**：禁止直接推送与强制推送，要求通过 PR 合并，并将 GitHub Actions 的 `PR checks` 设为必过状态检查。
   - **标签规则（`v*`）**：仅允许仓库管理员或发布维护者创建与删除，禁止强制更新。
2. 在 PyPI 项目设置（`https://pypi.org/manage/project/trigrams-toolkit/settings/publishing/`）中登记 GitHub Publisher：

| 字段 | 值 |
| --- | --- |
| Owner | `LINEBARRELS` |
| Repository name | `trigrams-toolkit` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

3. 在 GitHub 仓库的 `Settings -> Environments` 中创建环境 `pypi`。部署规则应允许 `vcli-*` 标签，现有的 `v*` 规则也覆盖这些标签。

#### 发布新版本步骤

1. 在 `dev` 上更新待发布对象的版本。发布工具包时运行 `python tasks.py bump X.Y.Z`。发布 CLI 时运行 `python tasks.py bump X.Y.Z --target cli`。
2. 在对应的更新记录中新增 `## X.Y.Z` 节。
3. 运行 `python tasks.py check` 和 `python tasks.py check-release --tag <tag>`，其中 `<tag>` 使用上表中该发布对象的标签格式。
4. 将提交推送到 `dev`，向 `main` 提交发版 PR。
5. 等待 `PR checks` 通过，再使用 **Merge Commit** 或 Fast-Forward 合并。
6. 切换到 `main` 并拉取发版提交。从该提交创建并推送对应的附注标签。
   ```sh
   git checkout main
   git pull --ff-only origin main
   git tag -a <tag> -m "Release <tag>"
   git push origin <tag>
   ```

工具包标签标记 GitHub 上的 Skill 和资源版本。CLI 标签触发 `Release to PyPI` 工作流，跨平台验收通过后上架 PyPI。

如需本地试发 TestPyPI 或应急手动上传，可使用 `python tasks.py publish --test`（或 `--dry-run` 预演）。
