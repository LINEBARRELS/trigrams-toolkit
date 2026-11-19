"""Installed Skill layouts and command shims for hermetic business tests."""
from __future__ import annotations

import os
from pathlib import Path
import shlex
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def profile_environment(profile: Path) -> dict[str, str]:
    return {"USERPROFILE" if os.name == "nt" else "HOME": str(profile),
            "CLAUDE_CONFIG_DIR": str(profile / ".claude")}


def write_skill(directory: Path, name: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Fixture Skill\n---\n", encoding="utf-8")


def copy_core(profile: Path) -> Path:
    root = profile / ".agents/skills"
    for name in ("principles", "workbook"):
        shutil.copytree(ROOT / "skills" / name, root / name)
    return root


def copy_extension(project: Path, provider: str) -> Path:
    root = project / ".agents/skills"
    for source in (ROOT / "extensions" / provider / "skills").iterdir():
        if (source / "SKILL.md").is_file():
            shutil.copytree(source, root / source.name, dirs_exist_ok=True)
    return root / f"extension-setup-{provider}" / "assets"


def offline_global_skills(root: Path) -> dict[str, str]:
    profile = root / "profile"
    for name in ("archify", "smell-check"):
        write_skill(profile / ".agents/skills" / name, name)
    binary = root / "bin"
    write_source_commands(binary, {"npx": [sys.executable, "-c", "raise SystemExit(97)"]})
    return {**profile_environment(profile), "PATH": str(binary) + os.pathsep + os.environ.get("PATH", "")}


def source_commands() -> dict[str, list[str]]:
    installed = os.environ.get("TRIGRAMS_INSTALLED_BIN")
    modules = {"project-state": "state.cli", "plan-toolkit": "plan.cli",
               "handbook": "handbook.cli", "harness-install": "installation.harness_install"}
    if installed:
        return {name: [str(Path(installed) / (name + (".exe" if os.name == "nt" else "")))] for name in modules}
    return {name: [sys.executable, "-B", "-m", "trigrams_toolkit." + module] for name, module in modules.items()}


def write_source_commands(bin_root: Path, commands: dict[str, list[str]]) -> None:
    """Wire subprocess lookup locally; these are test shims, not distribution entry points."""
    bin_root.mkdir(parents=True, exist_ok=True)
    for name, command in commands.items():
        if os.name == "nt":
            quoted = " ".join('"' + part + '"' for part in command)
            (bin_root / (name + ".cmd")).write_text(f"@echo off\n{quoted} %*\n", encoding="utf-8")
        else:
            path = bin_root / name
            path.write_text("#!/bin/sh\nexec " + shlex.join(command) + ' "$@"\n', encoding="utf-8")
            path.chmod(0o755)
