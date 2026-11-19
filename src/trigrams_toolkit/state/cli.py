"""Project State's JSON/stdout/exit-code boundary."""
from __future__ import annotations

import json
import sys
from typing import Sequence

from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.version import version
from .arguments import parse_arguments
from .help import help_text
from .service import execute


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        invocation = parse_arguments(sys.argv[1:] if argv is None else argv)
        if invocation.kind == "help":
            print(help_text(invocation.command), end="")
            return 0
        if invocation.kind == "version":
            print(version())
            return 0
        response = {"ok": True, "data": execute(invocation)}
    except ProtocolError as error:
        response = {"ok": False, "error": error.state_error()}
    except (OSError, ValueError, TypeError, RecursionError) as error:
        response = {"ok": False, "error": {"code": "io_error", "message": str(error)}}
    output = json.dumps(response, ensure_ascii=False, allow_nan=False)
    print(output.encode("utf-8", errors="backslashreplace").decode("utf-8"))
    return 0 if response["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
