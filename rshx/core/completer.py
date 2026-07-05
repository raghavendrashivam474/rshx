"""
completer.py
------------
Provides tab completion for RSHX.

Two completion sources are merged:
1. BuiltinCompleter  - completes built-in command names.
2. PathCompleter     - completes filesystem paths for arguments.

RshxCompleter combines both and decides which to activate
based on cursor position in the input buffer:
- First token  -> BuiltinCompleter
- Subsequent   -> PathCompleter
"""

from prompt_toolkit.completion import (
    Completer,
    Completion,
    PathCompleter,
    merge_completers,
)
from prompt_toolkit.document import Document

from rshx.commands.builtins import BUILTIN_REGISTRY


# ---------------------------------------------------------------------------
# Built-in completer
# ---------------------------------------------------------------------------

class BuiltinCompleter(Completer):
    """
    Complete built-in command names from BUILTIN_REGISTRY.

    Only activates when completing the first token on the line
    (the command name itself).
    """

    def get_completions(
        self,
        document: Document,
        complete_event,
    ):
        word = document.get_word_before_cursor()

        for name in sorted(BUILTIN_REGISTRY.keys()):
            if name.startswith(word):
                yield Completion(
                    text=name,
                    start_position=-len(word),
                    display_meta="built-in",
                )


# ---------------------------------------------------------------------------
# Combined completer
# ---------------------------------------------------------------------------

class RshxCompleter(Completer):
    """
    Route completion requests to the correct completer.

    Routing logic
    -------------
    - If the cursor is on the first token (no preceding whitespace
      before the word) -> BuiltinCompleter.
    - Otherwise -> PathCompleter (for arguments and paths).
    """

    def __init__(self) -> None:
        self._builtin = BuiltinCompleter()
        self._path = PathCompleter(expanduser=True)

    def get_completions(
        self,
        document: Document,
        complete_event,
    ):
        text_before_cursor = document.text_before_cursor

        # Determine whether we are completing the command name
        # or an argument by checking for whitespace before the cursor
        stripped = text_before_cursor.lstrip()
        is_first_token = " " not in stripped

        if is_first_token:
            yield from self._builtin.get_completions(document, complete_event)
        else:
            yield from self._path.get_completions(document, complete_event)
