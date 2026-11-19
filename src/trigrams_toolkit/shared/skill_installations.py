"""Filesystem locations used by the supported Vercel skills agents."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Final

from .errors import require
from .paths import confined, files_under, relative_path


@dataclass(frozen=True)
class SkillAgent:
    name: str
    directory: str


DEFAULT_AGENT: Final = "codex"
AGENTS: Final = {
    "codex": SkillAgent("codex", ".agents/skills"),
    "claude-code": SkillAgent("claude-code", ".claude/skills"),
    "pi": SkillAgent("pi", ".agents/skills"),
}


def skill_agent(name: str | None = None) -> SkillAgent:
    selected = name or DEFAULT_AGENT
    require(selected in AGENTS, "invalid_arguments",
            f"Unsupported Vercel skills agent: {selected}. Choose codex, claude-code or pi.")
    return AGENTS[selected]


def skill_directory(agent: SkillAgent, project: Path | None = None) -> Path:
    if project is not None:
        return confined(project, agent.directory)
    if agent.name == "claude-code" and (location := os.environ.get("CLAUDE_CONFIG_DIR", "").strip()):
        require(Path(location).is_absolute(), "invalid_arguments", "CLAUDE_CONFIG_DIR must be absolute.")
        return Path(location) / "skills"
    return Path.home() / agent.directory


def _same_tree(first: Path, second: Path) -> bool:
    # Vercel can create a second copy when a Claude link fails on Windows.
    files = {path.relative_to(first) for child in first.iterdir() for path in files_under(first, child)}
    return (files == {path.relative_to(second) for child in second.iterdir() for path in files_under(second, child)}
            and all((first / path).read_bytes() == (second / path).read_bytes() for path in files))


def installed_skill(name: str, agent: SkillAgent, project: Path | None = None,
                    *, required: bool = True) -> Path | None:
    relative_path(name)
    target = skill_directory(agent, project) / name
    scope = "global" if project is None else f"project ({project})"
    if not (target / "SKILL.md").is_file():
        require(not required, "missing_capability",
                f"Missing {scope} Skill {name} for {agent.name}: {target}. Install it with Vercel skills and retry.")
        return None
    root = target.resolve()
    confined(root, "SKILL.md")
    if agent.name == "claude-code":
        shared = (skill_directory(AGENTS["codex"], project) / name).resolve()
        if shared != root and (shared / "SKILL.md").is_file() and confined(shared, "SKILL.md").is_file():
            require(_same_tree(root, shared), "resource_conflict",
                    f"Different {scope} sources for Skill {name} ({agent.name}): {target}, {shared}. Reconcile the installations and retry.")
    return root
