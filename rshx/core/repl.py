"""
repl.py
-------
The Read-Evaluate-Print Loop - the heart of RSHX.

Sprint 2 changes
----------------
- Parser now returns PipelineNode instead of ParsedCommand.
- Executor accepts PipelineNode.
- Everything else unchanged.
"""

from dataclasses import dataclass, field
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings

from rshx.core.history import get_history
from rshx.core.completer import RshxCompleter
from rshx.core.prompt import build_prompt
from rshx.core.parser import parse
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
# Key bindings
# ---------------------------------------------------------------------------

def _build_key_bindings() -> KeyBindings:
    """Tab cycles through completions or triggers completion."""
    bindings = KeyBindings()

    @bindings.add("tab")
    def handle_tab(event):
        buffer = event.app.current_buffer
        if buffer.complete_state:
            buffer.complete_next()
        else:
            buffer.start_completion(select_first=True)

    return bindings


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def run_shell() -> None:
    """Start and run the RSHX interactive shell."""
    initialise_display()
    print_banner()

    state: ShellState = ShellState()
    completer: RshxCompleter = RshxCompleter(cwd_provider=lambda: state.cwd)

    session: PromptSession = PromptSession(
        history=get_history(),
        completer=completer,
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=False,
        key_bindings=_build_key_bindings(),
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
            pipeline = parse(raw_input)
        except ValueError as exc:
            print_error(str(exc))
            continue

        execute(pipeline, state)
        completer.update_cwd(state.cwd)
