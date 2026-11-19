"""Browse work guides and import approved principles into the project library."""
from __future__ import annotations

from trigrams_toolkit.version import version

from typing import NoReturn
import argparse
import json
from pathlib import Path
import sys

from trigrams_toolkit.shared.cli_help import HelpFormatter
from trigrams_toolkit.shared.errors import ProtocolError, require
from .guides import GuideCatalog
from .location import sources_for_project
from .principle_import import import_principle
from trigrams_toolkit.project_context import discover_project_root
from trigrams_toolkit.project_context.paths import resolve_project_path
from trigrams_toolkit.resources import schema_paths
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import read_json
from trigrams_toolkit.shared.skill_installations import AGENTS


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ProtocolError("invalid_arguments", message)


def _agent_option(parser: Parser) -> None:
    parser.add_argument("--agent", choices=AGENTS, default=argparse.SUPPRESS,
                        help="Vercel skills agent for global core resources; defaults to the project installation or codex.")


def _parser() -> Parser:
    parser = Parser(prog="handbook", description=__doc__,
                    formatter_class=HelpFormatter)
    _agent_option(parser)
    parser.add_argument("-v", "--version", action="store_true", help="Show the deployed toolkit version.")
    commands = parser.add_subparsers(dest="command", parser_class=Parser, title="Commands")
    descriptions = {"scopes": "List principle scope directories and workbook prefixes in the current project.",
                    "list": "List only resourceId and description for each guide.",
                    "load": "Read full IDs or unique short names, following workbook includes, with content and sources.",
                    "validate": "Check guide layout, headers, identities and includes references.",
                    "import-principle": "Import an approved draft into the project principle library."}
    for command, description in descriptions.items():
        child = commands.add_parser(command, help=description, description=description,
                                    formatter_class=HelpFormatter)
        _agent_option(child)
        if command in ("scopes", "list"):
            child.add_argument("--kind", choices=("workbook", "principle"), help="Only list this kind.")
        if command == "list":
            child.add_argument("--scope", action="append", default=[],
                               help="Match an exact scope from scopes; repeat for a union; omit for all guides.")
        if command == "load":
            child.add_argument("id", nargs="+", metavar="ID",
                               help="Full guide IDs or unique short names (scope/principle for principles).")
        if command == "import-principle":
            child.add_argument("file", type=Path, metavar="FILE", help="Approved UTF-8 draft; relative to the project root.")
            child.add_argument("--scope", required=True, help="Principle scope, using lowercase hyphenated tokens.")
            child.add_argument("--name", required=True, help="Principle name, using lowercase hyphenated tokens.")
            child.add_argument("--replace", action="store_true", help="Replace an existing principle; fail if absent.")
        child.epilog = ("Output: JSON with resourceId, entryPath and operation; exit 0 on success, 1 on error. "
                        "Existing targets require --replace. Write failures report error.current."
                        if command == "import-principle" else "Output: JSON; exit 0 on success, 1 on error.")
    return parser



def _catalog(root: Path, args: argparse.Namespace) -> GuideCatalog:
    schemas = SchemaCatalog(schema_paths())
    packages = sources_for_project(root, schemas, getattr(args, "agent", None))
    require(bool(packages), "missing_capability",
            "No guide sources are available. Install global principles and workbook Skills for the selected agent.")
    return GuideCatalog.discover(list(packages.values()), root, schemas)


def _dispatch(args: argparse.Namespace, root: Path) -> dict:
    if args.command == "import-principle":
        schemas = SchemaCatalog(schema_paths())
        source = resolve_project_path(root, args.file, cwd=Path.cwd(), confine=False)
        return import_principle(root, source, args.scope, args.name,
                                schemas, replace=args.replace, agent=getattr(args, "agent", None)).as_dict()
    catalog = _catalog(root, args)
    if args.command == "scopes":
        return catalog.scopes(args.kind)
    if args.command == "list":
        return catalog.list(args.kind, args.scope)
    if args.command == "load":
        return catalog.load(args.id)
    return catalog.validate()


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        parser = _parser()
        try:
            args = parser.parse_args(sys.argv[1:] if argv is None else argv)
        except SystemExit as status:
            return int(status.code or 0)
        if args.version:
            require(args.command is None, "invalid_arguments", "--version is a root command option.")
            print(version())
            return 0
        require(args.command is not None, "invalid_arguments", "Choose a command; use handbook --help.")
        result = _dispatch(args, discover_project_root())
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except ProtocolError as error:
        result = {"ok": False, "error": {"code": error.code, "message": str(error)}}
        if error.conflicts:
            result["error"]["conflicts"] = list(error.conflicts)
        if error.current is not None:
            result["error"]["current"] = error.current
    except (OSError, ValueError) as error:
        result = {"ok": False, "error": {"code": "io_error", "message": str(error)}}
    print(json.dumps(result, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
