"""Complete missing global Skills for the confirmed installation agent."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
from subprocess import DEVNULL, TimeoutExpired, run

from trigrams_toolkit.resources import resource_path
from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.serialization import read_json
from trigrams_toolkit.shared.skill_installations import SkillAgent, skill_directory


def _failure(agent: SkillAgent, name: str, reason: str, *, code: str = "dependency_failed") -> ProtocolError:
    return ProtocolError(code, f"Global Skill {name} for {agent.name}: {reason}",
                         details={"skill": name, "agent": agent.name})


def ensure_global_skills(agent: SkillAgent, project: Path) -> None:
    directory = skill_directory(agent)
    dependencies = read_json(resource_path("installation/global-skills.json"))["dependencies"]
    missing = [item for item in dependencies if not (directory / item["name"] / "SKILL.md").is_file()]
    if not missing:
        return
    npx = shutil.which("npx.cmd" if os.name == "nt" else "npx")
    if npx is None:
        raise _failure(agent, missing[0]["name"], "npx is unavailable. Install Node.js with npm and retry.",
                       code="missing_capability")

    for item in missing:
        name = item["name"]
        command = [npx, "-y", item["package"], "add", item["source"], "--skill", name,
                   "--agent", agent.name, "--global", "--copy", "--yes"]
        try:
            result = run(command, cwd=project, stdin=DEVNULL, check=False, capture_output=True,
                         encoding="utf-8", errors="replace", timeout=120,
                         env={**os.environ, "DISABLE_TELEMETRY": "1", "NO_COLOR": "1"})
        except (OSError, TimeoutExpired) as error:
            raise _failure(agent, name, str(error)) from error
        if result.returncode:
            reason = (result.stderr.strip() or result.stdout.strip() or f"Exit code {result.returncode}.")[-800:]
            raise _failure(agent, name, reason)
        if not (directory / name / "SKILL.md").is_file():
            raise _failure(agent, name, f"Installation did not create {directory / name / 'SKILL.md'}.")
