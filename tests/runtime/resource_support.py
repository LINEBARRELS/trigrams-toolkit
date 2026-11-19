"""Source invocation helpers for the guide CLI."""
from __future__ import annotations

import os
import subprocess
import sys

from support import ROOT, RuntimeCase

CLI = ROOT / "tests/runtime/resource_cli.py"


class ResourceCliCase(RuntimeCase):
    def cli(self, *arguments: str) -> tuple[int, dict | str]:
        import json
        result = subprocess.run([sys.executable, str(CLI), *arguments], cwd=self.project,
                                capture_output=True, text=True, encoding="utf-8",
                                env={**os.environ, "HARNESS_TOOLS_HOME": str(self.root / "tools")})
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = result.stdout
        return result.returncode, output
