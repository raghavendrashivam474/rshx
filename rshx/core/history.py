"""
history.py
----------
Manages persistent command history for RSHX.

Responsibilities
----------------
- Define the history file location.
- Provide a configured FileHistory instance for prompt_toolkit.
- Handle missing or corrupted history files gracefully.

prompt_toolkit's FileHistory class handles all read/write
operations automatically. This module's job is purely to
configure and expose it correctly.
"""

from pathlib import Path
from prompt_toolkit.history import FileHistory, InMemoryHistory


# ---------------------------------------------------------------------------
# History file location
# ---------------------------------------------------------------------------

HISTORY_DIR: Path = Path.home() / ".rshx"
HISTORY_FILE: Path = HISTORY_DIR / "history"


def get_history() -> FileHistory | InMemoryHistory:
    """
    Return a prompt_toolkit history object.

    Attempts to create and return a FileHistory backed by
    ~/.rshx/history. Falls back to InMemoryHistory if the
    directory cannot be created or the file cannot be accessed,
    so the shell always starts successfully regardless of
    filesystem state.

    Returns
    -------
    FileHistory | InMemoryHistory
        A prompt_toolkit history object ready for use in
        PromptSession.
    """
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)

        # Touch the file if it does not yet exist
        if not HISTORY_FILE.exists():
            HISTORY_FILE.touch()

        return FileHistory(str(HISTORY_FILE))

    except OSError:
        # Filesystem issue - fall back to in-memory history
        return InMemoryHistory()


def get_history_file_path() -> Path:
    """
    Return the path to the history file.

    Used by tests and diagnostics. Does not guarantee the
    file exists.

    Returns
    -------
    Path
        Absolute path to the history file.
    """
    return HISTORY_FILE
