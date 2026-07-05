"""
executor.py
-----------
Handles execution of parsed commands.

Execution flow
--------------
1. Check whether the command name matches a registered built-in.
2. If yes  — delegate to the built-in handler.
3. If no   — attempt to run the command as an external process via
             subprocess, inheriting the shell's current working
             directory.

Keeps execution strategy details out of the REPL so the REPL
remains a thin orchestration layer.
"""

import subprocess
from typing import TYPE_CHECKING

from rshx.commands.builtins import BUILTIN_REGISTRY
from rshx.core.parser import ParsedCommand
from rshx.utils.display import print_error, print_info

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


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _execute_builtin(
    command: ParsedCommand,
    shell_state: "ShellState",
) -> None:
    """
    Dispatch to the appropriate built-in command handler.

    Wraps the call in a try/except so that an unexpected error in a
    built-in command never crashes the entire REPL.
    """
    handler = BUILTIN_REGISTRY[command.name]
    try:
        handler(command.args, shell_state)
    except Exception as exc:                          # noqa: BLE001
        print_error(f"Built-in '{command.name}' raised an unexpected error: {exc}")


def _execute_external(
    command: ParsedCommand,
    shell_state: "ShellState",
) -> None:
    """
    Run an external system command as a child process.

    Design decisions
    ----------------
    - shell=False   : safer; avoids shell-injection risks.
    - cwd           : inherited from shell_state so that external
                      tools see the directory the user navigated to.
    - check=False   : we handle non-zero exit codes ourselves so we
                      can display a meaningful message.
    - FileNotFoundError  : command does not exist on PATH.
    - PermissionError    : binary exists but is not executable.
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
        print_error(
            f"Command not found: '{command.name}'. "
            "Check spelling or ensure the program is on your PATH."
        )

    except PermissionError:
        print_error(f"Permission denied: cannot execute '{command.name}'.")

    except Exception as exc:                          # noqa: BLE001
        print_error(f"Unexpected error while running '{command.name}': {exc}")
