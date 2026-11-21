# 第三方内容与素材

根目录 [MIT License](LICENSE) 适用于维护者有权授权的原创内容。第三方组件与素材遵循各自许可和来源声明。

## 外部 Skill

| 内容 | 来源 | 保留的许可 |
| --- | --- | --- |
| smell-check（必需外部依赖，不随包内嵌） | [Zhen-Bo/smell-check](https://github.com/Zhen-Bo/smell-check) | 使用上游安装包携带的许可 |
| answer-me-with-html（必需外部依赖，不随包内嵌） | [QingYunA/answer-me-with-html](https://github.com/QingYunA/answer-me-with-html) | 使用上游安装包携带的许可 |

上述 Skill 通过各自来源安装。`harness-install install apply` 检查并补齐目标 `agent` 缺失的 `answer-me-with-html` 与 `smell-check`。安装来源见[全局依赖声明](src/trigrams_toolkit/resources/installation/global-skills.json)。上游参考材料按其来源标注。

## Python CLI 运行依赖

运行依赖在 [pyproject.toml](pyproject.toml) 维护，由 uv／pip 安装原发行包及其许可。当前直接依赖均采用 MIT：PyYAML、jsonschema、referencing、ruamel.yaml。传递依赖包括 attrs、jsonschema-specifications、rpds-py，以及适用 Python 版本上的 typing-extensions、ruamel.yaml.clib；保留各发行包携带的许可文件。

每次候选包验收在 `.tmp/` 的 `package-check.json` 中记录实际安装版本与依赖闭包。开发用 build、setuptools、mypy 和类型声明属于开发依赖，随各自发行包保留许可。
