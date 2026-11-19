"""One installed program version, independent of data protocol versions."""
from importlib.metadata import version as distribution_version


def version() -> str:
    return distribution_version("trigrams-toolkit")
