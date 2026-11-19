"""Report process context and optionally hold a deployment lease for acceptance."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

from validation_info import VERSION


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ready", type=Path)
    parser.add_argument("--release", type=Path)
    parser.add_argument("--protocol", action="store_true", help="Echo arguments and JSON stdin; emit stderr and exit 23.")
    parser.add_argument("arguments", nargs="*")
    args = parser.parse_args()
    if args.protocol:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        print(json.dumps({"ok": False, "arguments": args.arguments, "input": json.load(sys.stdin),
                          "cwd": str(Path.cwd())}, ensure_ascii=False))
        print("protocol stderr 空间", file=sys.stderr)
        return 23
    if (args.ready is None) != (args.release is None):
        parser.error("--ready and --release must be provided together")
    if args.ready is not None:
        args.ready.write_text("ready", encoding="utf-8")
        deadline = time.monotonic() + 30
        while not args.release.is_file():
            if time.monotonic() >= deadline:
                raise TimeoutError("Lease acceptance did not release the process")
            time.sleep(0.05)
    print(json.dumps({"ok": True, "version": VERSION, "cwd": str(Path.cwd()),
                      "toolsRoot": os.environ.get("HARNESS_TOOLS_HOME")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
