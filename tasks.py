"""Repository development, build, verification and PyPI release tasks."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
DIRECT_WHEEL_DIR = ROOT / ".tmp/direct-wheel"
TEST_PYPI_URL = "https://test.pypi.org/legacy/"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?$")
PROJECT_SECTION_RE = re.compile(r"^\[project\]\s*$", re.MULTILINE)
SECTION_HEADER_RE = re.compile(r"^\[[^\]]+\]\s*$", re.MULTILINE)
VERSION_LINE_RE = re.compile(r'^(version\s*=\s*)(["\'])[^"\']*\2', re.MULTILINE)


def _project_metadata() -> tuple[str, str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    return str(project["name"]), str(project["version"])


def _expected_artifacts() -> tuple[str, Path, Path, Path]:
    name, version = _project_metadata()
    dist_name = name.replace("-", "_")
    sdist = DIST_DIR / f"{dist_name}-{version}.tar.gz"
    wheel = DIST_DIR / f"{dist_name}-{version}-py3-none-any.whl"
    direct_wheel = DIRECT_WHEEL_DIR / wheel.name
    return version, sdist, wheel, direct_wheel


def _run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def _cmd_check(_args: argparse.Namespace) -> None:
    _run([sys.executable, "scripts/verify_toolkit.py"])
    _run([sys.executable, "scripts/check_protocols.py"])
    _run([sys.executable, "-m", "mypy"])


def _declared_manifests(toolkit: dict) -> list[str]:
    manifests: list[str] = []
    core_manifest = toolkit.get("core", {}).get("manifest")
    if isinstance(core_manifest, str):
        manifests.append(core_manifest)
    for ext_data in toolkit.get("extensions", {}).values():
        ext_manifest = ext_data.get("manifest") if isinstance(ext_data, dict) else None
        if isinstance(ext_manifest, str):
            manifests.append(ext_manifest)
    return manifests


def _has_changelog_section(root: Path, version: str) -> bool:
    changelog_path = root / "CHANGELOG.md"
    if not changelog_path.is_file():
        return False
    text = changelog_path.read_text(encoding="utf-8")
    return bool(re.search(rf"^##\s+{re.escape(version)}(?:\s|$)", text, re.MULTILINE))


def _update_pyproject_version(text: str, version: str) -> str:
    header = PROJECT_SECTION_RE.search(text)
    if header is None:
        raise ValueError("pyproject.toml is missing a [project] section.")
    next_header = SECTION_HEADER_RE.search(text, header.end())
    end = next_header.start() if next_header else len(text)
    section = text[header.end():end]
    updated_section, count = VERSION_LINE_RE.subn(rf'\g<1>"{version}"', section, count=1)
    if count != 1:
        raise ValueError("pyproject.toml [project] section must declare a single version field.")
    updated = text[:header.end()] + updated_section + text[end:]
    if str(tomllib.loads(updated)["project"]["version"]) != version:
        raise ValueError("Updated pyproject.toml version check failed.")
    return updated


def bump_version(root: Path, version: str, *, dry_run: bool = False) -> dict:
    """Align pyproject.toml, toolkit.json and declared resource manifests to one version."""
    if not VERSION_RE.match(version):
        raise ValueError(f"Invalid version {version!r}; expected X.Y.Z without a 'v' prefix.")

    pyproject_path = root / "pyproject.toml"
    old_pyproject = pyproject_path.read_text(encoding="utf-8")
    new_pyproject = _update_pyproject_version(old_pyproject, version)
    staged: list[tuple[str, Path, str, bool]] = [
        ("pyproject.toml", pyproject_path, new_pyproject, new_pyproject != old_pyproject),
    ]

    toolkit_path = root / "toolkit.json"
    toolkit = json.loads(toolkit_path.read_text(encoding="utf-8"))
    for rel in ("toolkit.json", *_declared_manifests(toolkit)):
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(f"Missing manifest: {rel}")
        old_text = path.read_text(encoding="utf-8")
        data = json.loads(old_text)
        changed = data.get("version") != version
        data["version"] = version
        new_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        staged.append((rel, path, new_text if changed else old_text, changed))

    if not dry_run:
        for _, path, content, changed in staged:
            if changed:
                path.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "version": version,
        "dryRun": dry_run,
        "updated": [rel for rel, _, _, changed in staged if changed],
        "unchanged": [rel for rel, _, _, changed in staged if not changed],
        "changelogReady": _has_changelog_section(root, version),
    }


def check_release_metadata(root: Path = ROOT, *, tag: str | None = None, check_changelog: bool = True) -> dict:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    package = str(project["name"])
    version = str(project["version"])
    issues: list[str] = []
    checked: list[str] = ["pyproject.toml"]

    if tag is not None and tag != f"v{version}":
        issues.append(f"Git tag {tag!r} does not match pyproject.toml version {version!r} (expected 'v{version}').")

    toolkit_path = root / "toolkit.json"
    toolkit = json.loads(toolkit_path.read_text(encoding="utf-8"))
    checked.append("toolkit.json")
    if toolkit.get("version") != version:
        issues.append(f"toolkit.json version {toolkit.get('version')!r} != {version!r}.")

    for rel in _declared_manifests(toolkit):
        path = root / rel
        checked.append(rel)
        if not path.is_file():
            issues.append(f"Missing manifest: {rel}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("version") != version:
            issues.append(f"{rel} version {data.get('version')!r} != {version!r}.")

    if check_changelog:
        changelog_path = root / "CHANGELOG.md"
        checked.append("CHANGELOG.md")
        if not changelog_path.is_file():
            issues.append("Missing CHANGELOG.md.")
        elif not _has_changelog_section(root, version):
            issues.append(f"CHANGELOG.md does not contain a '## {version}' section.")

    return {
        "ok": not issues,
        "package": package,
        "version": version,
        "tag": tag,
        "checked": checked,
        "issues": issues,
    }


def _cmd_bump(args: argparse.Namespace) -> None:
    try:
        report = bump_version(ROOT, args.version, dry_run=args.dry_run)
    except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError) as error:
        print(json.dumps({"ok": False, "version": args.version, "error": str(error)}, ensure_ascii=False, indent=2))
        raise SystemExit(1) from error
    print(json.dumps(report, ensure_ascii=False, indent=2))


def _cmd_setup_hooks(_args: argparse.Namespace) -> None:
    hooks_dir = ROOT / ".githooks"
    if not hooks_dir.is_dir():
        raise SystemExit("Missing .githooks directory in repository root.")
    _run(["git", "config", "core.hooksPath", ".githooks"])
    print("Configured git core.hooksPath = .githooks")


def _cmd_check_release(args: argparse.Namespace) -> None:
    report = check_release_metadata(ROOT, tag=args.tag, check_changelog=not args.skip_changelog)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit(1)


def _cmd_test(_args: argparse.Namespace) -> None:
    _run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    _run([sys.executable, "-m", "unittest", "discover", "-s", "tests/runtime", "-v"])


def _cmd_build(args: argparse.Namespace) -> None:
    for path in (DIST_DIR, DIRECT_WHEEL_DIR, ROOT / ".tmp/build", ROOT / "src/trigrams_toolkit.egg-info"):
        if path.exists():
            shutil.rmtree(path)
    installer = ["--installer", "uv"] if shutil.which("uv") else []
    if not args.no_direct_wheel:
        _run([sys.executable, "-m", "build", "--wheel", *installer, "--outdir", str(DIRECT_WHEEL_DIR)])
    _run([sys.executable, "-m", "build", *installer, "--outdir", str(DIST_DIR)])
    _, sdist, wheel, _ = _expected_artifacts()
    print(f"Built release artifacts in {DIST_DIR}:")
    print(f"  - {sdist.name}")
    print(f"  - {wheel.name}")


def _require_dist_artifacts() -> tuple[str, Path, Path, Path]:
    version, sdist, wheel, direct_wheel = _expected_artifacts()
    missing = [path for path in (sdist, wheel) if not path.is_file()]
    if missing:
        names = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        raise SystemExit(f"Missing built artifacts for {version}: {names}. Run `python tasks.py build` first.")
    extras = sorted(
        path.name for path in DIST_DIR.iterdir()
        if path.is_file() and path.name not in {sdist.name, wheel.name}
    )
    if extras:
        raise SystemExit(f"Unexpected files in dist/: {', '.join(extras)}. Run `python tasks.py build` for a clean build.")
    return version, sdist, wheel, direct_wheel


def _cmd_verify_package(args: argparse.Namespace) -> None:
    _, sdist, wheel, direct_wheel = _require_dist_artifacts()
    command = [
        sys.executable, "scripts/check_package.py", str(wheel),
        "--sdist", str(sdist),
        "--output", str(args.output),
    ]
    if direct_wheel.is_file():
        command.extend(["--direct-wheel", str(direct_wheel)])
    if args.python:
        command.extend(["--python", args.python])
    if args.skip_business:
        command.append("--skip-business")
    _run(command)


def _cmd_publish(args: argparse.Namespace) -> None:
    version, sdist, wheel, _ = _require_dist_artifacts()
    tool = args.tool
    if tool == "auto":
        tool = "uv" if shutil.which("uv") else "twine"
    if tool == "uv":
        uv = shutil.which("uv")
        if uv is None:
            raise SystemExit("`uv` was not found on PATH. Install uv or pass --tool twine.")
        command = [uv, "publish", "--username", "__token__"]
        if (
            not os.environ.get("UV_PUBLISH_TOKEN")
            and not os.environ.get("UV_PUBLISH_PASSWORD")
            and not os.environ.get("UV_KEYRING_PROVIDER")
            and shutil.which("keyring") is not None
        ):
            command.extend(["--keyring-provider", "subprocess"])
        if args.test:
            command.extend(["--publish-url", TEST_PYPI_URL])
        command.extend([str(sdist), str(wheel)])
    else:
        command = [sys.executable, "-m", "twine", "upload", "--username", "__token__"]
        if args.test:
            command.extend(["--repository", "testpypi"])
        command.extend([str(sdist), str(wheel)])
    target = "TestPyPI" if args.test else "PyPI"
    print(f"Target: {target} (version {version})")
    if args.dry_run:
        print("Dry run:", " ".join(command))
        return
    _run(command)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tasks.py",
        description="Standard development, build, verification and PyPI release tasks for trigrams-toolkit.",
    )
    sub = parser.add_subparsers(dest="task", required=True)
    sub.add_parser("check", help="Run verify_toolkit, check_protocols and mypy.")
    bump = sub.add_parser(
        "bump",
        help="Align pyproject.toml, toolkit.json and resource manifests to a release version.",
    )
    bump.add_argument("version", help="Release version without leading 'v' (e.g. 0.3.3).")
    bump.add_argument("--dry-run", action="store_true", help="Report planned version updates without writing files.")
    sub.add_parser("setup-hooks", help="Configure git core.hooksPath to .githooks.")
    check_release = sub.add_parser(
        "check-release",
        help="Verify version alignment across pyproject.toml, manifests, CHANGELOG.md and an optional Git tag.",
    )
    check_release.add_argument("--tag", help="Expected Git release tag (e.g. v0.1.0).")
    check_release.add_argument("--skip-changelog", action="store_true", help="Skip checking CHANGELOG.md heading.")
    sub.add_parser("test", help="Run tests/ and tests/runtime/ unit test suites.")

    build = sub.add_parser("build", help="Clean and build sdist + wheel into dist/ (plus direct wheel in .tmp/).")
    build.add_argument("--no-direct-wheel", action="store_true", help="Skip the parity direct-wheel build in .tmp/.")

    verify = sub.add_parser("verify-package", help="Run isolated uv tool installation checks on dist/ artifacts.")
    verify.add_argument("--output", type=Path, default=Path(".tmp/package-check"), help="Verification receipt directory.")
    verify.add_argument("--python", help="Explicit Python interpreter passed to check_package.py.")
    verify.add_argument("--skip-business", action="store_true", help="Skip business acceptance tests.")

    publish = sub.add_parser("publish", help="Upload dist/ release artifacts to PyPI or TestPyPI.")
    publish.add_argument("--test", action="store_true", help="Upload to TestPyPI instead of PyPI.")
    publish.add_argument("--dry-run", action="store_true", help="Validate dist/ and print the publish command without uploading.")
    publish.add_argument("--tool", choices=("auto", "uv", "twine"), default="auto", help="Upload tool (default: auto).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    handlers = {
        "check": _cmd_check,
        "bump": _cmd_bump,
        "setup-hooks": _cmd_setup_hooks,
        "check-release": _cmd_check_release,
        "test": _cmd_test,
        "build": _cmd_build,
        "verify-package": _cmd_verify_package,
        "publish": _cmd_publish,
    }
    handlers[args.task](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
