"""Repository development, build, verification and PyPI release tasks."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
DIRECT_WHEEL_DIR = ROOT / ".tmp/direct-wheel"
TEST_PYPI_URL = "https://test.pypi.org/legacy/"


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
        "test": _cmd_test,
        "build": _cmd_build,
        "verify-package": _cmd_verify_package,
        "publish": _cmd_publish,
    }
    handlers[args.task](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
