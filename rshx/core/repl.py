"""
repl.py
-------
The Read-Evaluate-Print Loop - the heart of RSHX.

Sprint 1 changes
----------------
- PromptSession now receives history and completer.
- Prompt rendering delegated to core.prompt.
- History management delegated to core.history.
- Completion delegated to core.completer.
"""

from dataclasses import dataclass, field
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from rshx.core.history import get_history
from rshx.core.completer import RshxCompleter
from rshx.core.prompt import build_prompt
from rshx.core.parser import parse, ParsedCommand
from rshx.core.executor import execute
from rshx.utils.display import print_error, print_banner, initialise_display


# ---------------------------------------------------------------------------
# Shell state
# ---------------------------------------------------------------------------

@dataclass
class ShellState:
    """
    Mutable state that persists for the lifetime of the shell session.

    Attributes
    ----------
    cwd : Path
        The shell's current working directory.
    running : bool
        When set to False the REPL loop exits cleanly.
    """
    cwd: Path = field(default_factory=Path.cwd)
    running: bool = True


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def run_shell() -> None:
    """Start and run the RSHX interactive shell."""
    initialise_display()
    print_banner()

    state: ShellState = ShellState()

    session: PromptSession = PromptSession(
        history=get_history(),
        completer=RshxCompleter(),
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=False,
    )

    while state.running:
        try:
            raw_input: str = session.prompt(build_prompt(state.cwd))

        except KeyboardInterrupt:
            print()
            continue

        except EOFError:
            print()
            break

        try:
            command: ParsedCommand = parse(raw_input)
        except ValueError as exc:
            print_error(str(exc))
            continue

        execute(command, state)
