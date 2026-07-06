"""
repl.py
-------
The Read-Evaluate-Print Loop - the heart of RSHX.

Sprint 3 changes
----------------
- ShellState now holds AliasManager and Environment instances.
- Preprocessor is instantiated and called before parsing.
- Warnings from preprocessing are displayed to the user.
"""

from dataclasses import dataclass, field
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings

from rshx.core.alias_manager import AliasManager
from rshx.core.environment import Environment
from rshx.core.preprocessor import Preprocessor
from rshx.core.history import get_history
from rshx.core.completer import RshxCompleter
from rshx.core.prompt import build_prompt
from rshx.core.parser import parse
from rshx.core.executor import execute
from rshx.utils.display import (
    print_error,
    print_warning,
    print_banner,
    initialise_display,
)


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
    alias_manager : AliasManager
        The session alias registry.
    environment : Environment
        The session environment variable registry.
    """
    cwd: Path = field(default_factory=Path.cwd)
    running: bool = True
    alias_manager: AliasManager = field(default_factory=AliasManager)
    environment: Environment = field(default_factory=Environment)


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
    preprocessor: Preprocessor = Preprocessor(
        alias_manager=state.alias_manager,
        environment=state.environment,
    )
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

        # Preprocessing - alias and variable expansion
        try:
            expanded, warnings = preprocessor.process(raw_input)
        except Exception as exc:
            print_error(f"Preprocessor error: {exc}")
            continue

        for warning in warnings:
            print_warning(warning)

        # Parsing
        try:
            pipeline = parse(expanded)
        except ValueError as exc:
            print_error(str(exc))
            continue

        # Execution
        execute(pipeline, state)
        completer.update_cwd(state.cwd)
