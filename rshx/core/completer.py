"""
completer.py
------------
Provides tab completion for RSHX.

Completion behaviour
--------------------
- First token  : completes built-in command names inline
- After space  : completes filesystem paths inline

Behaves like a standard shell - Tab completes the longest
common prefix, repeated Tab cycles through matches.
"""

import os
from pathlib import Path

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_path_completions(prefix: str, cwd: Path) -> list[str]:
    """
    Return a list of filesystem paths matching the given prefix.

    Parameters
    ----------
    prefix : str
        The partial path typed by the user.
    cwd : Path
        The shell's current working directory.

    Returns
    -------
    list[str]
        Sorted list of matching path strings.
    """
    # Expand ~ to home directory
    expanded = os.path.expanduser(prefix)

    # Determine search directory and partial name
    if os.path.sep in expanded or "/" in expanded:
        search_dir = Path(expanded).parent
        partial = Path(expanded).name
    else:
        search_dir = cwd
        partial = expanded

    # Resolve relative paths against cwd
    if not search_dir.is_absolute():
        search_dir = cwd / search_dir

    try:
        entries = sorted(search_dir.iterdir())
    except (PermissionError, FileNotFoundError, OSError):
        return []

    matches = []
    for entry in entries:
        if entry.name.lower().startswith(partial.lower()):
            # Preserve the prefix style when building completion
            if os.path.sep in prefix or "/" in prefix:
                base = str(Path(prefix).parent)
                sep = os.path.sep
                candidate = f"{base}{sep}{entry.name}"
            else:
                candidate = entry.name

            # Append separator for directories so next Tab works
            if entry.is_dir():
                candidate += os.path.sep

            matches.append(candidate)

    return matches


# ---------------------------------------------------------------------------
# Built-in completer
# ---------------------------------------------------------------------------

class BuiltinCompleter(Completer):
    """Complete built-in command names on the first token."""

    def __init__(self, builtins: list[str]) -> None:
        self._builtins = sorted(builtins)

    def get_completions(self, document: Document, complete_event):
        word = document.get_word_before_cursor(WORD=True)
        for name in self._builtins:
            if name.startswith(word):
                yield Completion(
                    text=name,
                    start_position=-len(word),
                    display_meta="built-in",
                )


# ---------------------------------------------------------------------------
# Path completer
# ---------------------------------------------------------------------------

class ShellPathCompleter(Completer):
    """Complete filesystem paths for command arguments."""

    def __init__(self, cwd_provider) -> None:
        self._cwd_provider = cwd_provider

    def get_completions(self, document: Document, complete_event):
        word = document.get_word_before_cursor(WORD=True)
        cwd = self._cwd_provider()
        matches = _get_path_completions(word, cwd)

        for match in matches:
            yield Completion(
                text=match,
                start_position=-len(word),
            )


# ---------------------------------------------------------------------------
# Combined completer
# ---------------------------------------------------------------------------

class RshxCompleter(Completer):
    """
    Route completion to built-in or path completer based on
    cursor position in the input line.

    First token  -> BuiltinCompleter
    After space  -> ShellPathCompleter
    """

    def __init__(self, cwd_provider=None) -> None:
        from rshx.commands.builtins import BUILTIN_REGISTRY

        self._builtin = BuiltinCompleter(list(BUILTIN_REGISTRY.keys()))
        self._path = ShellPathCompleter(
            cwd_provider=cwd_provider or Path.cwd
        )

    def update_cwd(self, cwd: Path) -> None:
        """Update the working directory used by path completion."""
        self._path._cwd_provider = lambda: cwd

    def get_completions(self, document: Document, complete_event):
        text_before = document.text_before_cursor
        stripped = text_before.lstrip()
        is_first_token = " " not in stripped

        if is_first_token:
            yield from self._builtin.get_completions(document, complete_event)
        else:
            yield from self._path.get_completions(document, complete_event)
