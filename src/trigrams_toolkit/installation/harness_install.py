"""Project resource snapshots: read-only preview and idempotent apply."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import NoReturn, Sequence

from trigrams_toolkit.project_context import current_project_root
from trigrams_toolkit.resources import schema_paths as source_schema_paths
from trigrams_toolkit.shared.cli_help import help_requested
from trigrams_toolkit.shared.errors import ProtocolError, require
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import parse_json
from trigrams_toolkit.version import version
from .archive_project import archive_project
from .installation_candidate import build_candidate
from .installation_help import help_text
from .installation_service import apply_installation


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ProtocolError("invalid_arguments", message)


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments in (["-v"], ["--version"]):
        print(version())
        return 0
    parser = Parser(description=__doc__)
    parser.add_argument("group", choices=["install"])
    parser.add_argument("command", choices=["preview", "apply"])
    parser.add_argument("--input", required=True)
    parser.add_argument("--request-id")
    parser.add_argument("--expected-revision", type=int)
    operation, request_id = "install", None
    try:
        if help_requested(arguments):
            print(help_text("harness-install", arguments), end="")
            return 0
        if arguments and arguments[0] == "archive":
            return _archive(arguments[1:])
        for flag in ("--input", "--request-id", "--expected-revision"):
            require(sum(argument == flag or argument.startswith(flag + "=") for argument in arguments) <= 1,
                    "invalid_arguments", f"Duplicate option: {flag}")
        args = parser.parse_args(arguments)
        operation, request_id = "install " + args.command, args.request_id
        project = current_project_root()
        schemas = SchemaCatalog(source_schema_paths())
        data = parse_json(sys.stdin.buffer.read() if args.input == "-" else (project / args.input).read_bytes())
        require(isinstance(data, dict), "invalid_schema", "Installation input must be an object.")
        if args.command == "preview":
            require(args.request_id is None and args.expected_revision is None,
                    "invalid_arguments", "Preview rejects mutation options.")
            result = build_candidate(project, data, schemas).preview
        else:
            require(args.request_id is not None and args.expected_revision is not None,
                    "invalid_arguments", "Mutation requires request ID and expected revision.")
            result = apply_installation(project, data, schemas, args.request_id, args.expected_revision)
        response = {"ok": True, "operation": operation, "requestId": request_id, "data": result}
    except ProtocolError as error:
        response = {"ok": False, "operation": operation, "requestId": request_id, "error": error.as_dict()}
    except (OSError, ValueError) as error:
        response = {"ok": False, "operation": operation, "requestId": request_id,
                    "error": ProtocolError("io_error", str(error)).as_dict()}
    print(json.dumps(response, ensure_ascii=False))
    return 0 if response["ok"] else 1

def _archive(arguments: list[str]) -> int:
    parser = Parser(prog="harness-install archive", description="Archive selected project paths without reading their formats.")
    parser.add_argument("paths", nargs="+", help="Project-relative files or directories to archive.")
    try:
        args = parser.parse_args(arguments)
        response = {"ok": True, "data": archive_project(current_project_root(), args.paths)}
    except ProtocolError as error:
        response = {"ok": False, "error": error.as_dict()}
    except OSError as error:
        response = {"ok": False, "error": ProtocolError("io_error", str(error)).as_dict()}
    print(json.dumps(response, ensure_ascii=False))
    return 0 if response["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
