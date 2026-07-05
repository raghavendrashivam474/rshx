"""
repl.py
The Read-Evaluate-Print Loop - the heart of RSHX.
"""

from dataclasses import dataclass, field
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

from rshx.core.parser import parse, ParsedCommand
from rshx.core.executor import execute
from rshx.utils.display import print_error, print_banner, initialise_display


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


def _build_prompt(state: ShellState) -> HTML:
    """Build the prompt string shown to the user."""
    cwd_display: str = str(state.cwd)

    return HTML(
        f"<ansigreen><b>RSHX</b></ansigreen> "
        f"<ansicyan>{cwd_display}</ansicyan>"
        f"<ansiwhite> &gt; </ansiwhite>"
    )


def run_shell() -> None:
    """Start and run the RSHX interactive shell."""
    initialise_display()
    print_banner()

    state: ShellState = ShellState()
    session: PromptSession = PromptSession()

    while state.running:
        try:
            raw_input: str = session.prompt(_build_prompt(state))

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
