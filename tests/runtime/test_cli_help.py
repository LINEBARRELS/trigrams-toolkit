"""Public CLI help stays concise and works before project selection or mutation."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
from support import temporary_directory
from typing import Callable
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]

from trigrams_toolkit.plan.cli import main
from trigrams_toolkit.handbook.cli import main as global_main
from trigrams_toolkit.installation.harness_install import main as installation_main


class CliHelpTests(unittest.TestCase):
    def invoke(self, arguments: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with patch("trigrams_toolkit.plan.cli.discover_project_root", side_effect=AssertionError("Project IO")), redirect_stdout(output):
            code = main(arguments)
        return code, output.getvalue()

    def test_root_and_six_commands_have_equivalent_compact_help(self) -> None:
        for command in ("", "inspect", "mark", "block", "cancel", "validate", "get-task"):
            with self.subTest(command=command):
                arguments = [command] if command else []
                short = self.invoke([*arguments, "-h"])
                long = self.invoke([*arguments, "--help"])
                self.assertEqual(short, long)
                self.assertEqual(short[0], 0, short[1])
                self.assertIn("plan-toolkit" + (" " + command if command else ""), short[1])
                self.assertLessEqual(max(map(len, short[1].splitlines())), 100)
                self.assertNotIn("--input", short[1])
                self.assertNotIn("--request-id", short[1])
                self.assertNotIn("--expected-revision", short[1])
                self.assertNotIn("Session", short[1])

    def test_help_explains_positional_targets_and_state_options(self) -> None:
        root = self.invoke(["--help"])[1]
        for name in ("inspect", "mark", "block", "cancel", "validate", "get-task"):
            self.assertIn(name, root)
        mark = self.invoke(["mark", "--help"])[1]
        self.assertIn("PLAN [TASK] STATE", mark)
        self.assertIn("--note", mark)
        self.assertIn("project root", mark)
        self.assertNotIn("--config", mark)
        self.assertNotIn("--project", mark)
        self.assertIn("omit to target the Plan itself", mark)
        self.assertIn("New state: pending, doing, rework or done.", mark)
        block = self.invoke(["block", "--help"])[1]
        self.assertIn("--reason", block)
        self.assertNotIn("--note", block)
        validation = self.invoke(["validate", "--help"])[1]
        self.assertIn("--sync", validation)
        self.assertNotIn("TASK", validation)
        self.assertNotIn("--sync", self.invoke(["get-task", "--help"])[1])
        inspection = self.invoke(["inspect", "--help"])[1]
        self.assertIn("--full", inspection)
        self.assertIn("omitted by default", inspection)
        for command in ("mark", "block", "cancel", "validate", "get-task"):
            self.assertNotIn("--full", self.invoke([command, "--help"])[1])

    def test_version_is_plain_text_and_removed_help_command_is_an_error(self) -> None:
        code, version = self.invoke(["--version"])
        self.assertEqual(code, 0)
        self.assertRegex(version.strip(), r"^\d+\.\d+\.\d+")
        self.assertEqual(self.invoke(["-v"]), (code, version))
        code, output = self.invoke(["claim", "--help"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["error"]["code"], "invalid_arguments")

    def test_real_host_help_and_version_create_no_project_files(self) -> None:
        with temporary_directory(prefix="plan-help-") as directory:
            for command, arguments in (
                    ("plan-toolkit", ["--help"]), ("plan-toolkit", ["inspect", "--help"]),
                    ("plan-toolkit", ["mark", "--help"]), ("plan-toolkit", ["--version"]),
                    ("handbook", ["import-principle", "-h"]),
                    ("handbook", ["import-principle", "--help"])):
                with self.subTest(arguments=arguments):
                    result = subprocess.run(
                        [sys.executable, "-B", "-m", "trigrams_toolkit." + {"plan-toolkit": "plan.cli", "handbook": "handbook.cli"}[command], *arguments], cwd=directory, capture_output=True,
                        text=True, encoding="utf-8", timeout=20)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stderr, "")
            self.assertEqual(list(Path(directory).iterdir()), [])


class PublicCliHelpTests(unittest.TestCase):
    def invoke(self, entry: Callable[[list[str]], int], arguments: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output), \
                patch("trigrams_toolkit.handbook.cli.discover_project_root", side_effect=AssertionError("Project IO")), \
                patch("trigrams_toolkit.installation.harness_install.current_project_root", side_effect=AssertionError("Project IO")), \
                patch("trigrams_toolkit.installation.archive_project.archive_project", side_effect=AssertionError("Archive IO")):
            return_code = entry(arguments)
        return return_code, output.getvalue()

    def test_handbook_and_installation_help_at_every_level(self) -> None:
        for tool, entry, commands in (
                ("handbook", global_main, ("", "scopes", "list", "load", "validate", "import-principle")),
                ("harness-install", installation_main, ("", "install", "install preview", "install apply", "archive"))):
            for command in commands:
                with self.subTest(tool=tool, command=command):
                    short = self.invoke(entry, [*command.split(), "-h"])
                    self.assertEqual(short, self.invoke(entry, [*command.split(), "--help"]))
                    self.assertEqual(short[0], 0, short[1])
                    self.assertTrue(short[1].startswith(f"Usage: {tool}{' ' + command if command else ''} "))
                    self.assertIn("Options:\n", short[1])
                    self.assertIn("-h, --help", short[1])
                    self.assertLessEqual(max(map(len, short[1].splitlines())), 100)
                    self.assertLessEqual(len(short[1].splitlines()), 30)
        self.assertIn("project root", self.invoke(installation_main, ["-h"])[1])
        for entry in (global_main, installation_main):
            self.assertEqual(self.invoke(entry, ["-v"]), self.invoke(entry, ["--version"]))
        archive = self.invoke(installation_main, ["archive", "-h"])[1]
        self.assertIn("Arguments:\n", archive)
        self.assertIn("archive PATH [PATH ...]", archive)
        self.assertIn("exit 0", archive.lower())
        for command in ("scopes", "list", "load", "validate", "import-principle"):
            text = self.invoke(global_main, [command, "-h"])[1]
            self.assertNotIn("--config", text)
            self.assertNotIn("--project", text)
            self.assertNotIn("--source", text)
        load = self.invoke(global_main, ["load", "-h"])[1]
        self.assertIn("ID [ID ...]", load)
        self.assertIn("workbook includes", load)
        principle = self.invoke(global_main, ["import-principle", "-h"])[1]
        for value in ("FILE", "--scope", "--name", "--replace", "project root"):
            self.assertIn(value, principle)

    def test_installation_help_skips_option_values_at_any_command_position(self) -> None:
        expected = self.invoke(installation_main, ["install", "apply", "-h"])
        for arguments in (
                ["--input", "install", "install", "apply", "-h"],
                ["install", "--input", "archive", "apply", "-h"],
                ["--input=archive", "install", "apply", "-h"],
                ["install", "apply", "--request-id", "missing", "--input=-", "-h"]):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.invoke(installation_main, arguments), expected)
        for action in ("preview", "apply"):
            code, output = self.invoke(installation_main, ["install", action, "-h", "schema"])
            self.assertEqual(code, 0, output)
            self.assertIn("$defs", json.loads(output))
        code, output = self.invoke(installation_main, ["unknown", "-h"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["error"]["code"], "invalid_arguments")
