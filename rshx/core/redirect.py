"""
redirect.py
-----------
Manages file handles for stdin and stdout redirection.

Isolates all filesystem interaction from the pipeline executor.
The pipeline executor asks this module to open files and receives
back file handles ready for use with subprocess.Popen.

This separation means redirection behaviour can be changed or
extended without touching process management logic.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import IO

from rshx.core.ast import RedirectNode, RedirectType
from rshx.utils.display import print_error


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def open_stdin(node: RedirectNode) -> IO | int | None:
    """
    Open the stdin source for a command stage.

    Parameters
    ----------
    node : RedirectNode
        The command stage to resolve stdin for.

    Returns
    -------
    IO | int | None
        An open file handle, subprocess.PIPE sentinel, or None
        to indicate that stdin should be inherited from the shell.
    """
    if not node.has_stdin_redirect():
        return None

    path = Path(node.stdin_file)

    if not path.exists():
        print_error(f"redirect: input file not found: '{node.stdin_file}'")
        return None

    try:
        return open(path, "r", encoding="utf-8")
    except PermissionError:
        print_error(f"redirect: permission denied reading: '{node.stdin_file}'")
        return None
    except OSError as exc:
        print_error(f"redirect: cannot open '{node.stdin_file}': {exc}")
        return None


def open_stdout(node: RedirectNode) -> IO | None:
    """
    Open the stdout destination for a command stage.

    Parameters
    ----------
    node : RedirectNode
        The command stage to resolve stdout for.

    Returns
    -------
    IO | None
        An open file handle or None to indicate that stdout should
        be inherited or connected to a pipe.
    """
    if not node.has_stdout_redirect():
        return None

    path = Path(node.stdout_file)
    mode = _resolve_mode(node.stdout_mode)

    try:
        return open(path, mode, encoding="utf-8")
    except PermissionError:
        print_error(f"redirect: permission denied writing: '{node.stdout_file}'")
        return None
    except OSError as exc:
        print_error(f"redirect: cannot open '{node.stdout_file}': {exc}")
        return None


def close_handles(*handles) -> None:
    """
    Safely close one or more file handles.

    Ignores None values and handles that are already closed.
    Used to clean up after pipeline execution completes.

    Parameters
    ----------
    *handles
        Any number of file handles or None values.
    """
    for handle in handles:
        if handle is not None and not isinstance(handle, int):
            try:
                handle.close()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _resolve_mode(redirect_type: RedirectType | None) -> str:
    """
    Convert a RedirectType to a Python file open mode string.

    Parameters
    ----------
    redirect_type : RedirectType | None
        The redirect type to resolve.

    Returns
    -------
    str
        'w' for overwrite, 'a' for append.
    """
    if redirect_type == RedirectType.OUTPUT_APPEND:
        return "a"
    return "w"
