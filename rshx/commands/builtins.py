"""
builtins.py
-----------
Implements all built-in shell commands.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from rshx.core.theme import get_theme, list_themes, is_valid_theme
from rshx.core.confirmation import confirm_destructive
from rshx.utils.display import (
    print_output,
    print_success,
    print_error,
    print_info,
    print_warning,
)

if TYPE_CHECKING:
    from rshx.core.repl import ShellState


HELP_DATA: dict[str, dict[str, str]] = {
    "help": {
        "description": "Display help information for available commands.",
        "usage":       "help [command]",
        "examples":    "help\n  help cd\n  help run",
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
    "plugin": {
        "description": "Manage RSHX plugins.",
        "usage":       "plugin [list|info|enable|disable|reload] [name]",
        "examples":    "plugin list\n  plugin info hello\n  plugin enable hello\n  plugin disable hello",
        "notes":       "Use 'plugin list' to see all loaded plugins.",
    },
    "run": {
        "description": "Execute a .rshx script file.",
        "usage":       "run <script.rshx> [arg1 arg2 ...]",
        "examples":    "run hello.rshx\n  run greet.rshx Raghav\n  run deploy.rshx production",
        "notes":       "Scripts share the active shell state.\n"
                       "  Arguments are available as %1 %2 etc.\n"
                       "  Scripts stop on failure by default.\n"
                       "  Use @continue_on_error true to override.",
    },
}


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
    if not confirm_destructive("remove alias", name):
        print_info("  Operation cancelled.")
        return
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
    if not confirm_destructive("remove environment variable", name):
        print_info("  Operation cancelled.")
        return
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
    from rshx.core.config import CONFIG_FILE
    print_output(f"\n  Configuration file: {CONFIG_FILE}\n")


def cmd_plugin(args: list[str], shell_state: "ShellState") -> None:
    pm = getattr(shell_state, "plugin_manager", None)
    if pm is None:
        print_error("Plugin manager not available.")
        return

    if not args or args[0] == "list":
        plugins = pm.list_plugins()
        if not plugins:
            print_info("  No plugins loaded.")
            return
        print_output("")
        print_output("  Plugins:")
        print_output("  " + "-" * 50)
        for p in plugins:
            status = "enabled" if p["enabled"] else "disabled"
            print_output(f"  {p['name']:<15} v{p['version']:<10} [{status}]")
            print_output(f"  {'':15} {p['description']}")
        print_output("")
        return

    if args[0] == "info":
        if len(args) < 2:
            print_error("plugin info: requires a plugin name.")
            return
        info = pm.get_plugin_info(args[1])
        if info is None:
            print_error(f"plugin info: plugin '{args[1]}' not found.")
            return
        print_output("")
        print_output(f"  Name        : {info['name']}")
        print_output(f"  Version     : {info['version']}")
        print_output(f"  Description : {info['description']}")
        print_output(f"  Author      : {info['author']}")
        print_output(f"  Commands    : {', '.join(info['commands'])}")
        print_output(f"  Status      : {'enabled' if info['enabled'] else 'disabled'}")
        print_output(f"  Min RSHX    : {info['min_rshx_version']}")
        print_output("")
        return

    if args[0] == "enable":
        if len(args) < 2:
            print_error("plugin enable: requires a plugin name.")
            return
        if pm.enable(args[1]):
            print_success(f"Plugin '{args[1]}' enabled.")
        else:
            print_error(f"plugin enable: plugin '{args[1]}' not found or failed.")
        return

    if args[0] == "disable":
        if len(args) < 2:
            print_error("plugin disable: requires a plugin name.")
            return
        if pm.disable(args[1]):
            print_success(f"Plugin '{args[1]}' disabled.")
        else:
            print_error(f"plugin disable: plugin '{args[1]}' not found.")
        return

    if args[0] == "reload":
        if len(args) < 2:
            print_error("plugin reload: requires a plugin name.")
            return
        if pm.reload(args[1]):
            print_success(f"Plugin '{args[1]}' reloaded.")
        else:
            print_error(f"plugin reload: plugin '{args[1]}' failed to reload.")
        return

    print_error(f"plugin: unknown subcommand '{args[0]}'.")


def cmd_run(args: list[str], shell_state: "ShellState") -> None:
    if not args:
        print_error("run: requires a script path.", suggestion="Usage: run <script.rshx> [arg1 ...]")
        return

    script_path = args[0]
    script_args = args[1:]

    from rshx.core.script_loader import load_script
    from rshx.core.script_parser import parse_script
    from rshx.core.script_runtime import run_script
    from rshx.core.preprocessor import Preprocessor

    loaded, error = load_script(script_path, cwd=shell_state.cwd)
    if loaded is None:
        print_error(f"run: {error}")
        return

    node, parse_errors = parse_script(loaded.source, script_path=str(loaded.path))
    if parse_errors:
        for pe in parse_errors:
            if "Unknown directive" in pe.message:
                print_warning(pe.format())
            else:
                print_error(pe.format())
        if [e for e in parse_errors if "Unknown directive" not in e.message]:
            return

    if node.is_empty():
        print_info(f"  Script '{script_path}' contains no commands.")
        return

    preprocessor = Preprocessor(shell_state.alias_manager, shell_state.environment)
    result = run_script(node, shell_state, preprocessor, script_args)
    _display_script_result(result)


def _display_script_result(result) -> None:
    print_output("")
    print_output(f"  Script: {result.script_name}")
    print_output("  " + "-" * 40)
    print_output(f"  Commands executed : {result.commands_executed}")
    print_output(f"  Succeeded         : {result.commands_succeeded}")
    print_output(f"  Failed            : {result.commands_failed}")
    print_output(f"  Duration          : {result.duration:.2f}s")

    if result.success:
        print_success("Result: SUCCESS")
    else:
        print_error("Result: FAILED")
        for error in result.errors:
            print_output("")
            print_error(error.format())
    print_output("")


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
    "plugin":  cmd_plugin,
    "run":     cmd_run,
}
