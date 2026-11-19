"""Invoke handbook directly from its source entry point."""
from pathlib import Path
import sys

from trigrams_toolkit.handbook.cli import main as global_main

raise SystemExit(global_main(sys.argv[1:]))
