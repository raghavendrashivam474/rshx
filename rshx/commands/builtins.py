"""
builtins.py
-----------
Implements all built-in shell commands.

Sprint 3 additions
------------------
- alias    : create, list, or inspect aliases
- unalias  : remove an alias
- set      : create or list environment variables
- unset    : remove an environment variable
- env      : display environment variables

Each built-in is a plain function accepting:
    args        : list[str]   - positional arguments from the parser
    shell_state : ShellState  - mutable shell state object
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
# Help data
# ---------------------------------------------------------------------------

HELP_DATA: dict[str, dict[str, str]] = {
    "help": {
        "description": "Display help information for available commands.",
        "usage":       "help [command]",
        "examples":    "help\n  help cd\n  help alias",
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
    "alias": {
        "description": "Create or display aliases.",
        "usage":       "alias [name[=value]]",
        "examples":    "alias\n  alias gs\n  alias gs=git status",
        "notes":       "With no arguments, lists all aliases.\n"
                       "  With a name only, shows that alias.\n"
                       "  With name=value, creates the alias.",
    },
    "unalias": {
        "description": "Remove an alias.",
        "usage":       "unalias <name>",
        "examples":    "unalias gs",
        "notes":       "The alias must exist.",
    },
    "set": {
        "description": "Create or display environment variables.",
        "usage":       "set [NAME=value]",
        "examples":    "set\n  set PROJECTS=C:\\Projects\n  set EDITOR=code",
        "notes":       "With no arguments, lists all variables.\n"
                       "  Variables are referenced as %NAME% in commands.",
    },
    "unset": {
        "description": "Remove an environment variable.",
        "usage":       "unset <NAME>",
        "examples":    "unset PROJECTS",
        "notes":       "The variable must exist.",
    },
    "env": {
        "description": "Display environment variables.",
        "usage":       "env [NAME]",
        "examples":    "env\n  env PROJECTS",
        "notes":       "With no arguments, lists all variables.\n"
                       "  With a name, shows that variable's value.",
    },
}


# ---------------------------------------------------------------------------
# Built-in implementations
# ---------------------------------------------------------------------------

def cmd_help(args: list[str], shell_state: "ShellState") -> None:
    """Display help information."""
    if args:
        _show_command_help(args[0])
    else:
        _show_all_help()


def _show_all_help() -> None:
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
    print_output("  Examples :")
    for example in data["examples"].split("\n"):
        print_output(f"    {example.strip()}")
    print_output("")
    print_output("  Notes    :")
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


def cmd_alias(args: list[str], shell_state: "ShellState") -> None:
    """
    Create or display aliases.

    No args      : list all aliases
    One arg      : show alias or create if contains =
    """
    aliases = shell_state.alias_manager

    if not args:
        _list_aliases(aliases.all())
        return

    raw = " ".join(args)

    if "=" in raw:
        # Create alias
        eq_pos = raw.index("=")
        name = raw[:eq_pos].strip()
        value = raw[eq_pos + 1:].strip()

        if not name:
            print_error("alias: name cannot be empty.")
            return
        if not value:
            print_error("alias: value cannot be empty.")
            return

        try:
            aliases.set(name, value)
            print_success(f"Alias set: {name} = '{value}'")
        except ValueError as exc:
            print_error(f"alias: {exc}")
    else:
        # Show single alias
        name = raw.strip()
        value = aliases.get(name)
        if value is None:
            print_error(f"alias: '{name}' not found.")
        else:
            print_output(f"  {name} = '{value}'")


def _list_aliases(aliases: dict[str, str]) -> None:
    if not aliases:
        print_info("  No aliases defined.")
        return
    print_output("")
    print_output("  Aliases:")
    print_output("  " + "-" * 40)
    for name, value in sorted(aliases.items()):
        print_output(f"  {name:<15} = '{value}'")
    print_output("")


def cmd_unalias(args: list[str], shell_state: "ShellState") -> None:
    """Remove an alias."""
    if not args:
        print_error("unalias: requires a name argument.")
        return

    name = args[0]
    try:
        shell_state.alias_manager.remove(name)
        print_success(f"Alias '{name}' removed.")
    except KeyError:
        print_error(f"unalias: alias '{name}' not found.")


def cmd_set(args: list[str], shell_state: "ShellState") -> None:
    """
    Create or display environment variables.

    No args      : list all variables
    NAME=value   : set variable
    """
    env = shell_state.environment

    if not args:
        _list_variables(env.all())
        return

    raw = " ".join(args)

    if "=" in raw:
        eq_pos = raw.index("=")
        name = raw[:eq_pos].strip()
        value = raw[eq_pos + 1:]

        if not name:
            print_error("set: variable name cannot be empty.")
            return

        try:
            env.set(name, value)
            print_success(f"Variable set: {name} = '{value}'")
        except ValueError as exc:
            print_error(f"set: {exc}")
    else:
        print_error(
            f"set: invalid syntax. Use: set NAME=value"
        )


def cmd_unset(args: list[str], shell_state: "ShellState") -> None:
    """Remove an environment variable."""
    if not args:
        print_error("unset: requires a name argument.")
        return

    name = args[0]
    try:
        shell_state.environment.remove(name)
        print_success(f"Variable '{name}' removed.")
    except KeyError:
        print_error(f"unset: variable '{name}' not found.")


def cmd_env(args: list[str], shell_state: "ShellState") -> None:
    """Display environment variables."""
    env = shell_state.environment

    if not args:
        _list_variables(env.all())
        return

    name = args[0]
    value = env.get(name)

    if value is None:
        print_error(f"env: variable '{name}' not defined.")
    else:
        print_output(f"  {name} = '{value}'")


def _list_variables(variables: dict[str, str]) -> None:
    if not variables:
        print_info("  No variables defined.")
        return
    print_output("")
    print_output("  Environment Variables:")
    print_output("  " + "-" * 40)
    for name, value in sorted(variables.items()):
        print_output(f"  {name:<20} = '{value}'")
    print_output("")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

BUILTIN_REGISTRY: dict[str, callable] = {
    "help":    cmd_help,
    "clear":   cmd_clear,
    "pwd":     cmd_pwd,
    "cd":      cmd_cd,
    "exit":    cmd_exit,
    "alias":   cmd_alias,
    "unalias": cmd_unalias,
    "set":     cmd_set,
    "unset":   cmd_unset,
    "env":     cmd_env,
}
