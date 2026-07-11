"""
script_loader.py
----------------
Owns all filesystem interaction for .rshx script loading.

Responsibilities
----------------
- Resolve script paths (relative to cwd or absolute)
- Verify file existence
- Verify the path is a file not a directory
- Validate .rshx extension
- Read source text as UTF-8
- Return structured load result

The Script Loader must not parse commands or execute anything.
"""

from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass

SCRIPT_EXTENSION = ".rshx"


@dataclass
class LoadedScript:
    """
    The result of a successful script load operation.

    Attributes
    ----------
    path : Path
        Absolute resolved path to the script file.
    source : str
        Full UTF-8 source text of the script.
    """
    path: Path
    source: str


def load_script(
    script_path: str,
    cwd: Path | None = None,
) -> tuple[LoadedScript | None, str]:
    """
    Load a .rshx script file from disk.

    Resolves the path relative to cwd if not absolute.
    Validates existence, type, and extension.
    Reads source as UTF-8.

    Parameters
    ----------
    script_path : str
        Path to the script file as provided by the user.
    cwd : Path | None
        Current working directory for resolving relative paths.
        Defaults to Path.cwd() when None.

    Returns
    -------
    tuple[LoadedScript | None, str]
        (LoadedScript, "") on success.
        (None, error_message) on any failure.
    """
    base = cwd or Path.cwd()
    path = Path(script_path)

    if not path.is_absolute():
        path = base / path

    path = path.resolve()

    if not path.exists():
        return None, f"Script not found: '{script_path}'"

    if not path.is_file():
        return None, f"Path is not a file: '{script_path}'"

    if path.suffix.lower() != SCRIPT_EXTENSION:
        return None, (
            f"Invalid script extension '{path.suffix}'. "
            f"Expected '{SCRIPT_EXTENSION}'."
        )

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, f"Script file is not valid UTF-8: '{script_path}'"
    except OSError as exc:
        return None, f"Cannot read script file: {exc}"

    return LoadedScript(path=path, source=source), ""
