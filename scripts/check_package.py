"""Install a local wheel with uv and verify its runtime outside the checkout."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("project-state", "plan-toolkit", "handbook", "harness-install")
LICENSES = ("LICENSE", "THIRD_PARTY_NOTICES.md")


@contextmanager
def external_cwd(report):
    temporary = tempfile.TemporaryDirectory(prefix="trigrams-independent-cwd-")
    try:
        yield Path(temporary.name).resolve()
    finally:
        try:
            temporary.cleanup()
        except OSError as error:
            report["temporaryCleanup"] = {"path": temporary.name, "error": str(error)}


def _verify_contents(wheel: Path, sdist: Path | None, direct_wheel: Path | None) -> dict[str, int]:
    source = ROOT / "src/trigrams_toolkit"
    runtime = {
        path.relative_to(source.parent).as_posix()
        for path in source.rglob("*")
        if path.is_file() and path.suffix in (".py", ".typed", ".json", ".md", ".toml")
    }
    files = {}
    for candidate in (wheel, direct_wheel):
        if candidate is None:
            continue
        with zipfile.ZipFile(candidate) as archive:
            names = {entry.filename for entry in archive.infolist() if not entry.is_dir()}
        metadata = {name for name in names if name.partition("/")[0].endswith(".dist-info")}
        assert names - metadata == runtime, (candidate, runtime - names, names - metadata - runtime)
        for license_name in LICENSES:
            assert any(name.endswith(f".dist-info/licenses/{license_name}") for name in metadata), (candidate, license_name)
        files["wheel" if candidate == wheel else "directWheel"] = len(names)
    if sdist is not None:
        with tarfile.open(sdist, "r:gz") as archive:
            entries = [entry.name.split("/", 1) for entry in archive.getmembers() if entry.isfile()]
        assert entries and all(len(entry) == 2 and entry[0] == entries[0][0] for entry in entries), sdist
        names = {entry[1] for entry in entries}
        metadata = {name for name in names if name.startswith("src/trigrams_toolkit.egg-info/")}
        required = {*LICENSES, "pyproject.toml", "MANIFEST.in", "setup.cfg", "PKG-INFO", "docs/pypi-readme.md",
                    *("src/" + name for name in runtime)}
        assert required <= names and names - metadata - required <= {"README.md"}, (
            sdist, required - names, names - metadata - required)
        files["sdist"] = len(names)
    return files


def check(wheel: Path, output: Path, python: str, *, business: bool = True,
          sdist: Path | None = None, direct_wheel: Path | None = None) -> dict:
    started = time.monotonic()
    output.mkdir(parents=True, exist_ok=True)
    report: dict = {"ok": False, "wheel": str(wheel), "platform": platform.platform(), "python": python, "commands": []}
    environment = {key: value for key, value in os.environ.items() if key.upper() not in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV")}
    environment.update(UV_TOOL_DIR=str(output / "tools"), UV_TOOL_BIN_DIR=str(output / "bin"),
                       UV_CACHE_DIR=str(output / "cache"), UV_LINK_MODE="copy", PYTHONNOUSERSITE="1",
                       PYTHONUSERBASE=str(output / "user"), PYTHONDONTWRITEBYTECODE="1")

    def run(command: list[str], *, cwd: Path, input_text: str | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
        event = {"command": command, "cwd": str(cwd)}
        report["commands"].append(event)
        result = subprocess.run(command, cwd=cwd, env=environment, input=input_text, capture_output=True,
                                text=True, encoding="utf-8", timeout=timeout)
        event.update(exitCode=result.returncode, stdout=result.stdout, stderr=result.stderr)
        return result

    def success(result: subprocess.CompletedProcess) -> None:
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    try:
        report["packageFiles"] = _verify_contents(wheel, sdist, direct_wheel)
        uv = shutil.which("uv")
        assert uv is not None, "uv is required for isolated tool installation"
        success(run([uv, "tool", "install", "--force", "--python", python, str(wheel)], cwd=output))
        runtime = output / "tools/trigrams-toolkit" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        suffix = ".exe" if os.name == "nt" else ""
        commands = {tool: str(output / "bin" / (tool + suffix)) for tool in TOOLS}
        # Run the built entries from independent directories and keep evidence in output.
        with external_cwd(report) as cwd:
            assert not cwd.is_relative_to(ROOT), "The independence check needs a cwd outside the checkout"
            environment.update(PYTHONIOENCODING="cp1252")
            probe = """import json, sys, importlib.metadata as m
import trigrams_toolkit, yaml, jsonschema, referencing, ruamel.yaml
from trigrams_toolkit.resources import schema_paths, adapter_files
from trigrams_toolkit.shared.schema import SchemaCatalog
SchemaCatalog(schema_paths())
print(json.dumps({'package':trigrams_toolkit.__file__, 'paths':sys.path, 'version':m.version('trigrams-toolkit'),
 'python':sys.version, 'schemas':len(schema_paths()), 'adapters':len(adapter_files('codex')),
 'dependencies':{d.metadata['Name']:d.version for d in m.distributions()}}, ensure_ascii=True))
"""
            result = run([str(runtime), "-I", "-c", probe], cwd=cwd)
            success(result)
            report["runtime"] = json.loads(result.stdout)
            assert Path(report["runtime"]["package"]).is_relative_to(output / "tools")
            assert str(ROOT / "src") not in report["runtime"]["paths"]
            versions = []
            for tool in TOOLS:
                for flag in ("-v", "--version"):
                    result = run([commands[tool], flag], cwd=cwd)
                    success(result)
                    assert not result.stderr
                    versions.append(result.stdout.strip())
                helps = []
                for flag in ("-h", "--help"):
                    result = run([commands[tool], flag], cwd=cwd)
                    success(result)
                    assert result.stdout.startswith("Usage: " + tool) and not result.stderr
                    helps.append(result.stdout)
                assert helps[0] == helps[1]
            assert len(set(versions)) == 1 and versions[0] == report["runtime"]["version"]
            with tempfile.TemporaryDirectory(prefix="shell project 空间 ", dir=cwd) as directory:
                _shell_checks(commands, Path(directory), output, run, success, report)
            if business:
                environment.update(TRIGRAMS_INSTALLED_BIN=str(output / "bin"), TRIGRAMS_ACCEPTANCE_ROOT=str(cwd),
                                   TRIGRAMS_ACCEPTANCE_EVIDENCE=str(output / "business.json"))
                result = run([str(runtime), "-m", "unittest", "discover", "-s", str(ROOT / "tests"),
                              "-p", "test_source_acceptance.py", "-v"], cwd=cwd, timeout=600)
                success(result)
                report["business"] = json.loads((output / "business.json").read_text(encoding="utf-8"))["ok"]
            assert list(cwd.iterdir()) == [], "CLI wrote files into an unrelated cwd"
        report["ok"] = True
    except Exception as error:
        report["error"] = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
    finally:
        report["seconds"] = round(time.monotonic() - started, 3)
        (output / "package-check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def _shell_checks(commands, project, output, run, success, report):
    name = "中文 空格 'single' \"double\""
    shells = []
    pwsh = shutil.which("pwsh")
    bash = shutil.which("bash") if os.name != "nt" else None
    assert (pwsh if os.name == "nt" else bash), "The platform shell is required for entrypoint acceptance"
    if pwsh:
        shells.append(("pwsh", pwsh))
    if bash:
        shells.append(("bash", bash))
    report["shells"] = [name for name, _ in shells]
    for shell, executable in shells:
        if shell == "pwsh":
            script = output / "entry-check.ps1"
            script.write_text("param($cli, $name, $id)\n& $cli register module $name --id $id\nexit $LASTEXITCODE\n", encoding="utf-8")
            prefix = [executable, "-NoProfile", "-File", str(script)]
        else:
            script = output / "entry-check.sh"
            script.write_text('#!/bin/bash\n"$1" register module "$2" --id "$3"\nexit $?\n', encoding="utf-8")
            prefix = [executable, str(script)]
        result = run([*prefix, commands["project-state"], name, "module_" + shell], cwd=project)
        success(result)
        assert json.loads(result.stdout)["data"]["entity"]["name"] == name and not result.stderr
        empty = run([*prefix, commands["project-state"], "", "module_empty"], cwd=project)
        assert empty.returncode == 1 and json.loads(empty.stdout)["error"]["code"] == "invalid_arguments" and not empty.stderr
        if shell == "pwsh":
            stdin_script = output / "stdin-check.ps1"
            stdin_script.write_text("param($cli)\n"
                                    "$OutputEncoding = [Text.UTF8Encoding]::new($false)\n"
                                    "[Console]::InputEncoding = $OutputEncoding\n"
                                    "[Console]::In.ReadToEnd() | & $cli install preview --input -\n"
                                    "exit $LASTEXITCODE\n", encoding="utf-8")
            stdin_prefix = [executable, "-NoProfile", "-File", str(stdin_script)]
        else:
            stdin_script = output / "stdin-check.sh"
            stdin_script.write_text('#!/bin/bash\n"$1" install preview --input -\nexit $?\n', encoding="utf-8")
            stdin_prefix = [executable, str(stdin_script)]
        invalid = run([*stdin_prefix, commands["harness-install"]], cwd=project,
                      input_text='{"中文":"first", "中文":"duplicate"}')
        error = json.loads(invalid.stdout)["error"]
        assert invalid.returncode == 1 and error["code"] == "invalid_json" and "中文" in error["message"] and not invalid.stderr
    document = project / "docs/null-ownership.md"
    document.parent.mkdir(exist_ok=True)
    document.write_text("---\nartifact-id: artifact_null\nmoduleId: null\n---\n# Repair\n", encoding="utf-8")
    repaired = run([commands["project-state"], "register", "artifact", "docs/null-ownership.md"], cwd=project)
    success(repaired)
    assert json.loads(repaired.stdout)["data"]["changed"] and "moduleId:" not in document.read_text(encoding="utf-8")
    success(run([commands["project-state"], "validate"], cwd=project))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--sdist", type=Path)
    parser.add_argument("--direct-wheel", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--skip-business", action="store_true")
    args = parser.parse_args()
    interpreter = str(Path(args.python).resolve()) if Path(args.python).is_file() else args.python
    report = check(args.wheel.resolve(), args.output.resolve(), interpreter, business=not args.skip_business,
                   sdist=args.sdist, direct_wheel=args.direct_wheel)
    print(json.dumps({"ok": report["ok"], "evidence": str(args.output / "package-check.json"),
                      "error": str(report.get("error", {}).get("message", ""))[:400]}, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
