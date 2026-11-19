"""Source business acceptance with isolated projects and retained failure receipts."""
from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

from source_fixture import ROOT, copy_core, offline_global_skills, source_commands


class SourceAcceptance:
    """Run business contracts from source while the published Python package is built."""
    def __init__(self, evidence: Path | None, kind: str):
        self.evidence = evidence
        self.started = time.monotonic()
        self.case = "setup"
        self.temporary = None
        self.report = {"ok": False, "kind": kind, "source": str(ROOT),
                       "python": platform.python_version(), "platform": platform.platform(),
                       "revision": os.environ.get("GITHUB_SHA", "working-tree"), "phase": "setup",
                       "commands": [], "tests": []}

    def setup(self) -> None:
        fixture_root = Path(os.environ.get("TRIGRAMS_ACCEPTANCE_ROOT", ROOT / ".tmp"))
        fixture_root.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="source-acceptance-", dir=fixture_root)
        self.base = Path(self.temporary.name).resolve() / "tools and projects 空间"
        self.base.mkdir()
        self.source = self.base / "fixtures"
        self.skill_env = offline_global_skills(self.base)
        self.core = copy_core(self.base / "profile")
        self.help_cwd = self.base / "unrelated working directory"
        self.help_cwd.mkdir()
        self.extension = self.source / "extensions/validation"
        shutil.copytree(ROOT / "tests/fixtures/global-extension", self.extension,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.commands = source_commands()
        self.commands["harness-validation"] = [sys.executable, "-B", str(self.extension / "tools/validation_cli.py")]

    def configure_project(self, project: Path) -> None:
        self.project = project
        self.project.mkdir(exist_ok=True)
        self.env = {**os.environ, **self.skill_env, "PYTHONIOENCODING": "cp1252", "PYTHONDONTWRITEBYTECODE": "1"}

    def command(self, tool: str, arguments=()) -> list[str]:
        return [*self.commands[tool], *map(str, arguments)]

    def capture(self, arguments: list[str], input_text: str | None = None, timeout: float = 60, *, cwd: Path | None = None):
        cwd = cwd if cwd is not None else self.project
        event = {"case": self.case, "phase": self.report["phase"], "arguments": list(map(str, arguments)),
                 "input": input_text, "cwd": str(cwd)}
        self.report["commands"].append(event)
        started = time.monotonic()
        try:
            result = subprocess.run(arguments, cwd=cwd, env=self.env, input=input_text,
                                    capture_output=True, text=True, encoding="utf-8", timeout=timeout)
            event.update(exitCode=result.returncode, stdout=result.stdout, stderr=result.stderr)
            return result
        except Exception as error:
            event.update(error=type(error).__name__, message=str(error))
            raise
        finally:
            event["seconds"] = round(time.monotonic() - started, 3)

    def fail(self, error: Exception) -> None:
        self.report.update(ok=False, error={"type": type(error).__name__, "message": str(error),
                                           "traceback": traceback.format_exc()})

    def close(self) -> None:
        if self.temporary is not None:
            try:
                self.temporary.cleanup()
            except OSError as error:
                self.report["temporaryCleanup"] = {"path": self.temporary.name, "error": str(error)}
        self.report["seconds"] = round(time.monotonic() - self.started, 3)
        if self.evidence is not None:
            self.evidence.parent.mkdir(parents=True, exist_ok=True)
            self.evidence.write_text(json.dumps(self.report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
