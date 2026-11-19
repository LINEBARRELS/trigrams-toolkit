"""Side-effect-free help from package-owned command descriptions."""
from trigrams_toolkit.resources import resource_path
from trigrams_toolkit.shared.serialization import read_json
from trigrams_toolkit.shared.cli_help import help_rows, paragraph


def help_text(command: str) -> str:
    entries = read_json(resource_path("state/help.json"))
    options = [("-h, --help", "Show help.")]
    if command in entries:
        entry = entries[command]
        lines = [paragraph("Usage: project-state " + entry["usage"]), "", paragraph(entry["summary"])]
        if entry.get("details"):
            lines.extend(["", paragraph(entry["details"])])
        return "\n".join([*lines, "", "Options:", *help_rows([*entry.get("options", []), *options]), "",
                          "Output: JSON; exit 0 on success, 1 on error.", ""])
    names = [name for name in entries if not command or name.startswith(command + " ")]
    rows = [(name[len(command) + 1:] if command else name, entries[name]["summary"]) for name in names]
    if not command:
        options.append(("-v, --version", "Show toolkit version."))
    prefix = "project-state" + (" " + command if command else "")
    return "\n".join([f"Usage: {prefix} COMMAND [options]", "",
                      "Run commands from the project root to manage architecture entities and relations.",
                      "", "Commands:", *help_rows(rows), "", "Options:", *help_rows(options), "",
                      f"Use {prefix} COMMAND -h for command details.", ""])
