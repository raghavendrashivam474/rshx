"""
builtins.py
-----------
Implements all built-in shell commands.

Each built-in is a plain function accepting:
    args        : list[str]   - positional arguments from the parser
    shell_state : ShellState  - mutable shell state object

Adding a new built-in requires only:
1. Writing the function.
2. Adding it to BUILTIN_REGISTRY.
3. Adding its help entry to HELP_DATA.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from rshx.utils.display import (
    print_output,
    print_success,
    print_error,
    print_info,
    print_warning,
)

if TYPE_CHECKING:
    from rshx.core.repl import ShellState


# ---------------------------------------------------------------------------
# Help data - drives the enhanced help system
# ---------------------------------------------------------------------------

HELP_DATA: dict[str, dict[str, str]] = {
    "help": {
        "description": "Display help information for available commands.",
        "usage":       "help [command]",
        "examples":    "help\n  help cd\n  help exit",
        "notes":       "Run 'help' with no arguments to list all commands.",
    },
    "clear": {
        "description": "Clear the terminal screen.",
        "usage":       "clear",
        "examples":    "clear",
        "notes":       "Equivalent to 'cls' on Windows and 'clear' on Unix.",
    },
    "pwd": {
        "description": "Print the current working directory.",
        "usage":       "pwd",
        "examples":    "pwd",
        "notes":       "Reflects the shell's internal working directory.",
    },
    "cd": {
        "description": "Change the current working directory.",
        "usage":       "cd [path]",
        "examples":    "cd ..\n  cd Documents\n  cd ~\n  cd C:\\Projects",
        "notes":       "With no arguments, navigates to the home directory.\n"
                       "  Supports ~ expansion and relative paths.",
    },
    "exit": {
        "description": "Exit the RSHX shell.",
        "usage":       "exit",
        "examples":    "exit",
        "notes":       "You can also press Ctrl-D to exit.",
    },
}


# ---------------------------------------------------------------------------
# Built-in implementations
# ---------------------------------------------------------------------------

def cmd_help(args: list[str], shell_state: "ShellState") -> None:
    """
    Display help information.

    With no arguments: list all built-in commands.
    With one argument: show detailed help for that command.
    """
    if args:
        _show_command_help(args[0])
    else:
        _show_all_help()


def _show_all_help(  ) -> None:
    """Print a summary table of all available built-in commands."""
    print_output("")
    print_output("  Built-in commands:")
    print_output("  " + "-" * 44)

    for name, data in HELP_DATA.items():
        print_output(f"  {name:<10} {data['description']}")

    print_output("")
    print_info("  Run 'help <command>' for detailed information.")
    print_info("  Any other input is treated as an external system command.")
    print_output("")


def _show_command_help(command: str) -> None:
    """Print detailed help for a single command."""
    if command not in HELP_DATA:
        print_error(f"help: no help available for '{command}'")
        print_info("  Run 'help' to see all available commands.")
        return

    data = HELP_DATA[command]

    print_output("")
    print_output(f"  Command : {command}")
    print_output("  " + "-" * 44)
    print_output(f"  {data['description']}")
    print_output("")
    print_output(f"  Usage    : {data['usage']}")
    print_output("")
    print_output(f"  Examples :")
    for example in data["examples"].split("\n"):
        print_output(f"    {example.strip()}")
    print_output("")
    print_output(f"  Notes    :")
    for note in data["notes"].split("\n"):
        print_output(f"    {note.strip()}")
    print_output("")


def cmd_clear(args: list[str], shell_state: "ShellState") -> None:
    """Clear the visible terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def cmd_pwd(args: list[str], shell_state: "ShellState") -> None:
    """Print the shell's current working directory."""
    print_output(str(shell_state.cwd))


def cmd_cd(args: list[str], shell_state: "ShellState") -> None:
    """Change the shell's current working directory."""
    if len(args) > 1:
        print_error("cd: too many arguments")
        return

    if not args:
        target: Path = Path.home()
    else:
        raw_path: str = args[0]
        target = Path(raw_path).expanduser()

        if not target.is_absolute():
            target = shell_state.cwd / target

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

    try:
        os.chdir(target)
        shell_state.cwd = target
    except PermissionError:
        print_error(f"cd: permission denied: {target}")


def cmd_exit(args: list[str], shell_state: "ShellState") -> None:
    """Set the shell running flag to False to trigger a clean exit."""
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
