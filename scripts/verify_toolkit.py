"""Validate source resources, public contracts and platform entry references."""
from __future__ import annotations

import ast
import argparse
from collections.abc import Iterator
import json
import os
from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
from trigrams_toolkit.installation.package_metadata import frontmatter
from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.handbook.source_catalog import validate_source_catalog

IGNORED = {"node_modules", "__pycache__", ".venv", "dist", "bin", ".git", ".cache",
           ".pytest_cache", ".smell-check", ".harness", ".harness-archive", ".agents", ".codex", ".claude", ".pi"}
ROOT_FILES = ("AGENTS.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE", "README.md",
              "THIRD_PARTY_NOTICES.md", "toolkit.json", "pyproject.toml", "MANIFEST.in", "setup.cfg", "tasks.py")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


SOURCE_DIRECTORIES = ("skills", "src", "extensions", "scripts", "tests", "docs", ".github")


def source_files(root: Path) -> Iterator[Path]:
    """Scan maintained source roots without Git, pruning before descent."""
    yield from (root / name for name in ROOT_FILES if (root / name).is_file())
    for source in SOURCE_DIRECTORIES:
        for directory, children, files in os.walk(root / source):
            children[:] = [name for name in children
                           if name not in IGNORED and not name.startswith(".tmp")]
            yield from (Path(directory) / name for name in files)


def historical_document(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if relative.parts[:3] == ("docs", "knowledge", "retrospectives"):
        return True
    if relative.parts[:2] != ("docs", "plans") or len(relative.parts) < 4:
        return False
    snapshot = root / "docs/plans" / relative.parts[2] / "plan.json"
    if not snapshot.is_file():
        return False
    return json.loads(snapshot.read_text(encoding="utf-8"))["status"] in ("done", "cancelled")


def _validate_skills(root: Path, components: list[dict]) -> tuple[list[str], list[str]]:
    issues, skills = [], []
    for component in components:
        if "skills" not in component:
            continue
        for skill in sorted((root / component["skills"]).iterdir()):
            if not skill.is_dir():
                continue
            entry = skill / "SKILL.md"
            if not entry.exists():
                issues.append(f"Missing SKILL.md: {skill}")
                continue
            data = frontmatter(entry)
            if data.get("name") != skill.name or not data.get("description"):
                issues.append(f"Invalid Skill identity: {entry}")
            skills.append(skill.name)
            for path in skill.rglob("*"):
                relative = path.relative_to(skill)
                if ("_runtime" in relative.parts or relative.parts[:2] == ("contracts", "runtime")
                        or relative.parts[0] == "verification" or path.suffix.lower() in (".exe", ".zip")):
                    issues.append(f"Retired Skill packaging remains: {path}")
                if path.name in ("extension.json", "resources.json", "provider.json") and relative.as_posix() != "assets/extension.json":
                    issues.append(f"Extension declaration must be in setup assets: {path}")
    if len(set(skills)) != len(skills):
        issues.append("Duplicate Skill names")
    return issues, skills


def _validate_sources(root: Path) -> tuple[list[str], int]:
    issues, links = [], 0
    for path in source_files(root):
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8-sig"))
            except SyntaxError as error:
                issues.append(f"{path}: {error}")
        if path.suffix != ".md" or historical_document(path, root):
            continue
        for match in LINK.finditer(path.read_text(encoding="utf-8-sig")):
            url = match.group(1).strip().removeprefix("<").removesuffix(">")
            if re.match(r"^[a-z][a-z0-9+.-]*:", url, re.I) or url.startswith("#"):
                continue
            target = unquote(url.split("#", 1)[0])
            if target and not (path.parent / target).exists():
                issues.append(f"Broken resource link: {path.relative_to(root)} -> {target}")
            links += 1
    return issues, links


def _validate_adapters(root: Path) -> list[str]:
    issues = []
    for platform, suffix in (("codex", ".toml"), ("claude", ".md"), ("pi-web", ".md")):
        for path in (root / "src/trigrams_toolkit/resources/adapters" / platform).glob("*" + suffix):
            if path.name == "README.md":
                continue
            source = path.read_text(encoding="utf-8")
            data = tomllib.loads(source) if suffix == ".toml" else frontmatter(path)
            if data.get("name") != path.stem or (suffix == ".toml" and not data.get("developer_instructions")):
                issues.append(f"Invalid {platform} role: {path.name}")
            if platform == "pi-web" and data.get("load_skills") is not True:
                issues.append(f"Pi Web role must load Skills: {path.name}")
            skill_refs = re.findall(r"使用 ([a-z][a-z0-9-]*) Skill", source)
            if not skill_refs or any(not (root / "skills" / ref / "SKILL.md").is_file() for ref in skill_refs):
                issues.append(f"Missing core Skill reference: {path}")
    return issues


def validate() -> dict:
    catalog = validate_source_catalog(ROOT)
    manifest = json.loads((ROOT / "toolkit.json").read_text(encoding="utf-8"))
    components = [manifest["core"], *manifest["extensions"].values()]
    issues, skills = _validate_skills(ROOT, components)
    source_issues, links = _validate_sources(ROOT)
    issues.extend(source_issues)
    issues.extend(_validate_adapters(ROOT))
    return {"ok": not issues, "skills": sorted(skills), "resources": catalog["resources"],
            "sources": catalog["sources"], "local_links": links,
            "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, width=100, max_help_position=30),
        epilog="Output: JSON validation counts and issues; read-only. Exit 0 when valid, 1 otherwise.")
    parser.parse_args()
    try:
        result = validate()
    except (ProtocolError, OSError, ValueError, KeyError) as error:
        result = {"ok": False, "issues": [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
