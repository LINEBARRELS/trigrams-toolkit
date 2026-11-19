"""Validate, inspect and schedule Plans with concise JSON results."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import NoReturn, Sequence

from trigrams_toolkit.project_context import discover_project_root
from trigrams_toolkit.project_context.paths import resolve_project_path
from trigrams_toolkit.shared.cli_help import HelpFormatter
from trigrams_toolkit.shared.errors import ProtocolError, require
from trigrams_toolkit.state import locate_identity
from trigrams_toolkit.version import version
from .model import JsonObject, MARK_STATES, Status
from .service import PlanService


@dataclass(frozen=True)
class Invocation:
    operation: str
    plan: Path
    target: str | None
    project_root: Path
    record: JsonObject | None = None
    sync: bool = False
    full: bool = False


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ProtocolError("invalid_arguments", message)


def parser() -> Parser:
    root = Parser(prog="plan-toolkit", description="Validate Plan handoffs and record current state.",
                  formatter_class=HelpFormatter)
    root.add_argument("-v", "--version", action="version", version=version())
    commands = root.add_subparsers(dest="operation", required=True, title="Commands")
    for operation, description in (
            ("validate", "Check declarations, progress and completion; optionally sync the snapshot."),
            ("get-task", "List Tasks eligible to start using current Stub and Task progress."),
            ("inspect", "Read concise Plan or Task status; use --full for the complete view."),
            ("mark", "Record pending, doing, rework or done."),
            ("block", "Record a blocking reason."),
            ("cancel", "Record a cancellation reason.")):
        command = commands.add_parser(operation, help=description, description=description,
                                      formatter_class=HelpFormatter,
                                      epilog="Output: JSON; exit 0 on success, 1 on error.")
        command.add_argument("plan", metavar="PLAN", type=Path, help="Plan directory within the current project root.")
        if operation not in ("validate", "get-task"):
            command.add_argument("target", metavar="TASK", nargs="?",
                                 help="Task directory ID, for example T01; omit to target the Plan itself.")
        if operation == "validate":
            command.add_argument("--sync", action="store_true", help="Compile declarations, preserving existing progress.")
        elif operation == "inspect":
            command.add_argument("--full", action="store_true",
                                 help="Include declarations, paths and Task/Stub bodies omitted by default.")
        if operation == "mark":
            command.add_argument("state", metavar="STATE", choices=MARK_STATES,
                                 help="New state: pending, doing, rework or done.")
            command.add_argument("--note", help="Optional note for this state.")
        elif operation in ("block", "cancel"):
            command.add_argument("--reason", required=True, help="Reason; for a block, include where to continue.")
    return root


def _record(args: argparse.Namespace) -> JsonObject | None:
    if args.operation in ("inspect", "validate", "get-task"):
        return None
    state = args.state if args.operation == "mark" else (
        Status.BLOCKED if args.operation == "block" else Status.CANCELLED)
    result = {"status": state}
    for field in ("note", "reason"):
        text = getattr(args, field, None)
        if text is not None:
            require(bool(text.strip()), "invalid_arguments", f"--{field} must not be empty.")
            result[field] = text
    return result


def parse_invocation(argv: Sequence[str]) -> Invocation:
    args = parser().parse_args(argv)
    record = _record(args)
    project_root = discover_project_root()
    plan = resolve_project_path(project_root, args.plan, cwd=Path.cwd())
    return Invocation(args.operation, plan, getattr(args, "target", None), project_root, record,
                      sync=getattr(args, "sync", False), full=getattr(args, "full", False))


def locate_spec(identity: str, invocation: Invocation) -> JsonObject:
    try:
        return {"id": identity, **locate_identity(invocation.project_root, identity)}
    except ProtocolError as error:
        return {"id": identity, "error": error.state_error()}
    except (OSError, ValueError, TypeError, RecursionError) as error:
        return {"id": identity, "error": {"code": "io_error", "message": str(error)}}


def dispatch(invocation: Invocation) -> JsonObject:
    service = PlanService(invocation.plan)
    if invocation.operation == "validate":
        return service.validate(sync=invocation.sync)
    if invocation.operation == "get-task":
        return service.get_tasks()
    if invocation.operation == "inspect":
        return service.inspect(invocation.target, lambda identity: locate_spec(identity, invocation),
                               full=invocation.full)
    require(invocation.record is not None, "invalid_arguments", "A state change requires a current-state record.")
    assert invocation.record is not None
    return service.update(invocation.target, invocation.record)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        invocation = parse_invocation(arguments)
        response = {"ok": True, "data": dispatch(invocation)}
    except SystemExit as result:
        return int(result.code or 0)
    except ProtocolError as error:
        issues = getattr(error, "issues", [{"code": error.code, "message": str(error)}])
        response = {"ok": False, "error": {"code": error.code, "message": str(error), "issues": issues}}
    except (OSError, UnicodeError) as error:
        response = {"ok": False, "error": {"code": "io_error", "message": str(error)}}
    print(json.dumps(response, ensure_ascii=False, allow_nan=False))
    return 0 if response["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
