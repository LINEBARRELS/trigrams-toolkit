# trigrams-toolkit

Command-line tools, schemas and core types for **Trigrams toolkit**.

## Requirements

- Python 3.11 or newer

## Installation

Install or upgrade the CLI package globally with `uv`:

```sh
uv tool install -U trigrams-toolkit
```

Or install with `pip`:

```sh
python -m pip install trigrams-toolkit
```

## Included CLI Commands

| Command | Purpose |
| --- | --- |
| `project-state` | Register and query project Modules, Features, Artifacts and relations in `.project-state/state.json`. |
| `plan-toolkit` | Compile plan snapshots, inspect task dependencies, list runnable tasks and track Plan / Task status. |
| `handbook` | Discover, load, validate and import workbooks and principles from global Skills, installed extensions and project resources. |
| `harness-install` | Preview and apply project extension snapshots (`.agents/extensions/`), ensure required global Skills, and archive explicit project paths. |

## Quick Usage

Help (`-h` / `--help`) and version (`-v` / `--version`) can be queried from any directory:

```sh
project-state --version
project-state --help
plan-toolkit --help
handbook --help
harness-install --help
```

All other subcommands operate on the current working directory and should be run from the target project root.

## Links

- Source & Skills: https://github.com/LINEBARRELS/trigrams-toolkit
- Issues: https://github.com/LINEBARRELS/trigrams-toolkit/issues

## License

MIT. See the bundled `LICENSE` and `THIRD_PARTY_NOTICES.md` files for details.
