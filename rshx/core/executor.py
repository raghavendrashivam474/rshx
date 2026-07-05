"""
executor.py
-----------
Handles execution of parsed commands.

Execution flow
--------------
1. Check whether the command matches a registered built-in.
2. If yes  - delegate to the built-in handler.
3. If no   - attempt to run as an external process via subprocess.
4. On failure - display a suggestion if a close match exists.
"""

import subprocess
import shutil
from typing import TYPE_CHECKING

from rshx.commands.builtins import BUILTIN_REGISTRY
from rshx.core.parser import ParsedCommand
from rshx.utils.display import print_error, print_info, suggest_command

if TYPE_CHECKING:
    from rshx.core.repl import ShellState


def execute(command: ParsedCommand, shell_state: "ShellState") -> None:
    """
    Execute a ParsedCommand against the current shell state.

    Parameters
    ----------
    command : ParsedCommand
        The structured command produced by the parser.
    shell_state : ShellState
        Mutable shell state providing cwd and running flag.
    """
    if command.is_empty():
        return

    if command.name in BUILTIN_REGISTRY:
        _execute_builtin(command, shell_state)
    else:
        _execute_external(command, shell_state)


def _execute_builtin(
    command: ParsedCommand,
    shell_state: "ShellState",
) -> None:
    """Dispatch to the appropriate built-in command handler."""
    handler = BUILTIN_REGISTRY[command.name]
    try:
        handler(command.args, shell_state)
    except Exception as exc:
        print_error(f"Built-in '{command.name}' raised an unexpected error: {exc}")


def _execute_external(
    command: ParsedCommand,
    shell_state: "ShellState",
) -> None:
    """
    Run an external system command as a child process.

    On FileNotFoundError, builds a candidate list from built-ins
    and PATH executables and offers a suggestion.
    """
    argv: list[str] = [command.name, *command.args]

    try:
        result: subprocess.CompletedProcess = subprocess.run(
            argv,
            cwd=shell_state.cwd,
            shell=False,
            check=False,
        )

        if result.returncode != 0:
            print_info(
                f"Process '{command.name}' exited with code {result.returncode}."
            )

    except FileNotFoundError:
        candidates = list(BUILTIN_REGISTRY.keys())
        suggest_command(command.name, candidates)

    except PermissionError:
        print_error(f"Permission denied: cannot execute '{command.name}'.")

    except Exception as exc:
        print_error(f"Unexpected error while running '{command.name}': {exc}")
