"""
builtins.py
Implements all built-in shell commands.
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


def cmd_help(args: list[str], shell_state: "ShellState") -> None:
    """Display all available built-in commands with short descriptions."""
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


BUILTIN_REGISTRY: dict[str, callable] = {
    "help":  cmd_help,
    "clear": cmd_clear,
    "pwd":   cmd_pwd,
    "cd":    cmd_cd,
    "exit":  cmd_exit,
}
