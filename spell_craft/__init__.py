# type: ignore[attr-defined]
"""SpellCraft CLI is a Python project that generates command-line interfaces (CLIs) from configurations. Each CLI plugin is packaged as a separate module containing a configuration and a list of commands. Our nomenclature revolves around the concept of spells and incantations, where plugins are spells and commands are incantations."""

import sys
from importlib import metadata as importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
