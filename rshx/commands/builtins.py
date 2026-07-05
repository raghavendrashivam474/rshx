"""
builtins.py
-----------
Implements all built-in shell commands.

Built-in commands run inside the RSHX process itself rather than
spawning a child process.  This gives them direct access to shell
state such as the current working directory.

Each built-in is a plain function that accepts:
    args        : list[str]   — positional arguments from the parser
    shell_state : ShellState  — mutable shell state object

Functions return None.  Output is produced via display utilities.
Adding a new built-in requires only adding a function and
registering it in BUILTIN_REGISTRY at the bottom of this module.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from rshx.utils.display import (
    print_output,
    print_success,
    print_error,
    print_info,
)

if TYPE_CHECKING:
    from rshx.core.repl import ShellState


# ---------------------------------------------------------------------------
# Individual built-in implementations
# ---------------------------------------------------------------------------

def cmd_help(args: list[str], shell_state: "ShellState") -> None:
    """
    Display all available built-in commands with short descriptions.
    Future sprints can extend this to show command-specific help
    when a command name is passed as an argument.
    """
    help_text: dict[str, str] = {
        "help":  "Show this help message",
        "clear": "Clear the terminal screen",
        "pwd":   "Print the current working directory",
        "cd":    "Change the current working directory  (usage: cd <path>)",
        "exit":  "Exit RSHX",
    }

    print_output("")
    print_output("  Built-in commands:")
    print_output("  " + "-" * 40)

    for command, description in help_text.items():
        print_output(f"  {command:<10} {description}")

    print_output("")
    print_info("  Any other input is treated as an external system command.")
    print_output("")


def cmd_clear(args: list[str], shell_state: "ShellState") -> None:
    """
    Clear the visible terminal screen.
    Uses the platform-appropriate system clear command.
    """
    os.system("cls" if os.name == "nt" else "clear")


def cmd_pwd(args: list[str], shell_state: "ShellState") -> None:
    """
    Print the shell's current working directory.
    Reads from shell_state rather than os.getcwd() so the value
    is always consistent with what the shell tracks internally.
    """
    print_output(str(shell_state.cwd))


def cmd_cd(args: list[str], shell_state: "ShellState") -> None:
    """
    Change the shell's current working directory.

    Behaviour
    ---------
    - No arguments : change to the user's home directory.
    - One argument : change to the specified path.
    - More than one argument : error.

    The change is reflected in shell_state.cwd AND in the
    process-level working directory via os.chdir so that external
    commands spawned by subprocess inherit the correct directory.
    """
    if len(args) > 1:
        print_error("cd: too many arguments")
        return

    # Resolve target directory
    if not args:
        target: Path = Path.home()
    else:
        raw_path: str = args[0]

        # Support ~ expansion
        target = Path(raw_path).expanduser()

        # Resolve relative paths against the shell's current directory
        if not target.is_absolute():
            target = shell_state.cwd / target

    # Resolve symlinks and normalise the path
    try:
        target = target.resolve(strict=True)
    except FileNotFoundError:
        print_error(f"cd: no such file or directory: {args[0] if args else ''}")
        return
    except PermissionError:
        print_error(f"cd: permission denied: {args[0] if args else ''}")
        return

    if not target.is_dir():
        print_error(f"cd: not a directory: {args[0] if args else ''}")
        return

    # Apply the directory change
    try:
        os.chdir(target)
        shell_state.cwd = target
    except PermissionError:
        print_error(f"cd: permission denied: {target}")


def cmd_exit(args: list[str], shell_state: "ShellState") -> None:
    """
    Set the shell running flag to False, triggering a clean exit
    from the REPL loop on the next iteration.
    """
    print_success("Goodbye!")
    shell_state.running = False


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

BUILTIN_REGISTRY: dict[str, callable] = {
    "help":  cmd_help,
    "clear": cmd_clear,
    "pwd":   cmd_pwd,
    "cd":    cmd_cd,
    "exit":  cmd_exit,
}
