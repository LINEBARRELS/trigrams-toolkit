"""Command help for project installation and explicit path archival."""
from pathlib import Path
from typing import Sequence

from trigrams_toolkit.shared.cli_help import HelpSchemas, render_help
from trigrams_toolkit.resources import resource_path, schema_paths
from trigrams_toolkit.shared.serialization import read_json

FIELDS = {
    "agent": "Vercel agent: codex, claude-code or pi. Omitted uses the project record or codex.",
    "packages": "Explicit absolute source roots for local development.",
    "extensions": "Selected extension names; omit to retain, or pass [] to remove all.",
    "preview": "Exact reviewed preview returned by install preview.",
    "confirmedBy": "Approver identity: {id, kind}; kind is human, agent or service.",
}


def options(mutation: bool) -> list[tuple[str, str]]:
    rows = [
        ("--input FILE|-", "Required. UTF-8 JSON file, or - for stdin."),
    ]
    if mutation:
        rows.extend([("--request-id req_ID", "Required. Latest write identity; an identical successful retry returns its receipt."),
                     ("--expected-revision N", "Required. Use the preview baseRevision.")])
    return rows


def help_text(tool: str, argv: Sequence[str]) -> str:
    commands = read_json(resource_path("installation/commands.json"))["commands"]
    for item in commands:
        action = item["name"].split()[-1]
        if action == "archive":
            item.update(summary="Move selected paths into .harness-archive without parsing their contents.",
                        usage="PATH [PATH ...]", options=[],
                        arguments=[("PATH", "Project-relative file or directory; repeat for multiple paths.")],
                        notes="Run from the target project root.",
                        result="JSON data contains the archive directory and original relative paths.")
            continue
        item.update(summary={"preview": "Compute a read-only, offline preview before project changes.",
                             "apply": "Apply reviewed changes; keep one backup and roll back write errors."}[action],
                    usage="--input FILE|- [options]", options=options(item["mutation"]), fields=FIELDS,
                    group_summary="Preview and install project resource snapshots.",
                    notes={"preview": "Run from the target project root. The preview binds apply to this directory.",
                           "apply": "Run from the project root used for preview. Apply may install missing Skills "
                                    "in the selected agent's global Skill directory."}[action],
                    result={"preview": "JSON data is the preview; retain it and baseRevision for apply.",
                            "apply": "JSON data contains operationId, phase, changed and stateRevision."}[action])
    return render_help(tool, argv, commands, HelpSchemas(schema_paths()))
