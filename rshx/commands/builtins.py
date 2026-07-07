"""
builtins.py
-----------
Implements all built-in shell commands.

Sprint 4 additions
------------------
- alias / unalias now persist via ConfigManager
- set / unset now persist via ConfigManager
- theme command to switch themes
- startup command to manage startup commands
- config command to show configuration file path
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from rshx.core.theme import get_theme, list_themes, is_valid_theme
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
        "notes":       "Reflects the shell internal working directory.",
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
        "notes":       "Aliases are persisted across sessions.\n"
                       "  With no arguments, lists all aliases.\n"
                       "  With name=value, creates the alias.",
    },
    "unalias": {
        "description": "Remove an alias.",
        "usage":       "unalias <name>",
        "examples":    "unalias gs",
        "notes":       "The alias is removed from persistent storage.",
    },
    "set": {
        "description": "Create or display environment variables.",
        "usage":       "set [NAME=value]",
        "examples":    "set\n  set PROJECTS=C:\\Projects\n  set EDITOR=code",
        "notes":       "Variables are persisted across sessions.\n"
                       "  Referenced as %NAME% in commands.",
    },
    "unset": {
        "description": "Remove an environment variable.",
        "usage":       "unset <NAME>",
        "examples":    "unset PROJECTS",
        "notes":       "The variable is removed from persistent storage.",
    },
    "env": {
        "description": "Display environment variables.",
        "usage":       "env [NAME]",
        "examples":    "env\n  env PROJECTS",
        "notes":       "With no arguments, lists all variables.\n"
                       "  With a name, shows that variable value.",
    },
    "theme": {
        "description": "Set or display the active shell theme.",
        "usage":       "theme [name]",
        "examples":    "theme\n  theme dark\n  theme light\n  theme default",
        "notes":       "Available themes: default, dark, light.\n"
                       "  Theme is persisted across sessions.",
    },
    "startup": {
        "description": "Manage startup commands.",
        "usage":       "startup [add|remove|list] [command]",
        "examples":    "startup list\n  startup add alias gs=git status\n  startup remove alias gs=git status",
        "notes":       "Startup commands run automatically when RSHX launches.",
    },
    "config": {
        "description": "Show configuration file location.",
        "usage":       "config",
        "examples":    "config",
        "notes":       "The configuration file is in TOML format.",
    },
}


# ---------------------------------------------------------------------------
# Built-in implementations
# ---------------------------------------------------------------------------

def cmd_help(args: list[str], shell_state: "ShellState") -> None:
    if args:
        _show_command_help(args[0])
    else:
        _show_all_help()


def _show_all_help() -> None:
    print_output("")
    print_output("  Built-in commands:")
    print_output("  " + "-" * 44)
    for name, data in HELP_DATA.items():
        print_output(f"  {name:<12} {data['description']}")
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
    os.system("cls" if os.name == "nt" else "clear")


def cmd_pwd(args: list[str], shell_state: "ShellState") -> None:
    print_output(str(shell_state.cwd))


def cmd_cd(args: list[str], shell_state: "ShellState") -> None:
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
    print_success("Goodbye!")
    shell_state.running = False


def cmd_alias(args: list[str], shell_state: "ShellState") -> None:
    aliases = shell_state.alias_manager
    cfg = shell_state.config_manager

    if not args:
        _list_aliases(aliases.all())
        return

    raw = " ".join(args)

    if "=" in raw:
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
            cfg.save_alias(name, value)
            print_success(f"Alias set: {name} = '{value}'")
        except ValueError as exc:
            print_error(f"alias: {exc}")
    else:
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
    if not args:
        print_error("unalias: requires a name argument.")
        return
    name = args[0]
    try:
        shell_state.alias_manager.remove(name)
        shell_state.config_manager.delete_alias(name)
        print_success(f"Alias '{name}' removed.")
    except KeyError:
        print_error(f"unalias: alias '{name}' not found.")


def cmd_set(args: list[str], shell_state: "ShellState") -> None:
    env = shell_state.environment
    cfg = shell_state.config_manager

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
            cfg.save_variable(name, value)
            print_success(f"Variable set: {name} = '{value}'")
        except ValueError as exc:
            print_error(f"set: {exc}")
    else:
        print_error("set: invalid syntax. Use: set NAME=value")


def cmd_unset(args: list[str], shell_state: "ShellState") -> None:
    if not args:
        print_error("unset: requires a name argument.")
        return
    name = args[0]
    try:
        shell_state.environment.remove(name)
        shell_state.config_manager.delete_variable(name)
        print_success(f"Variable '{name}' removed.")
    except KeyError:
        print_error(f"unset: variable '{name}' not found.")


def cmd_env(args: list[str], shell_state: "ShellState") -> None:
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


def cmd_theme(args: list[str], shell_state: "ShellState") -> None:
    """Set or display the active theme."""
    if not args:
        current = shell_state.config_manager.config.theme
        print_output(f"\n  Active theme : {current}")
        print_output(f"  Available    : {', '.join(list_themes())}\n")
        return

    name = args[0].lower()

    if not is_valid_theme(name):
        print_error(
            f"theme: '{name}' is not a valid theme. "
            f"Available: {', '.join(list_themes())}"
        )
        return

    shell_state.config_manager.set_theme(name)
    shell_state.theme = get_theme(name)
    print_success(f"Theme set to '{name}'.")


def cmd_startup(args: list[str], shell_state: "ShellState") -> None:
    """Manage startup commands."""
    cfg = shell_state.config_manager

    if not args or args[0] == "list":
        commands = cfg.config.startup_commands
        if not commands:
            print_info("  No startup commands defined.")
        else:
            print_output("")
            print_output("  Startup commands:")
            print_output("  " + "-" * 40)
            for i, cmd in enumerate(commands, 1):
                print_output(f"  {i}. {cmd}")
            print_output("")
        return

    if args[0] == "add":
        if len(args) < 2:
            print_error("startup add: requires a command argument.")
            return
        command = " ".join(args[1:])
        cfg.add_startup_command(command)
        print_success(f"Startup command added: '{command}'")
        return

    if args[0] == "remove":
        if len(args) < 2:
            print_error("startup remove: requires a command argument.")
            return
        command = " ".join(args[1:])
        cfg.remove_startup_command(command)
        print_success(f"Startup command removed: '{command}'")
        return

    print_error(
        f"startup: unknown subcommand '{args[0]}'. "
        "Use: startup list | add <cmd> | remove <cmd>"
    )


def cmd_config(args: list[str], shell_state: "ShellState") -> None:
    """Show configuration file path."""
    from rshx.core.config import CONFIG_FILE
    print_output(f"\n  Configuration file: {CONFIG_FILE}\n")


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
    "theme":   cmd_theme,
    "startup": cmd_startup,
    "config":  cmd_config,
}
