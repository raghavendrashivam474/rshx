"""
hello plugin
------------
Demonstrates the RSHX Plugin Framework.

Registers two commands:
- hello  : print a greeting
- greet  : greet a named person
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rshx.core.plugin_api import PluginAPI
    from rshx.core.repl import ShellState

_api = None


def initialise(api: "PluginAPI") -> None:
    """Register plugin commands with the shell."""
    global _api
    _api = api

    api.register_command(
        name="hello",
        handler=_cmd_hello,
        description="Print a greeting from the plugin framework.",
    )

    api.register_command(
        name="greet",
        handler=_cmd_greet,
        description="Greet a named person.",
    )

    api.register_help(
        command="hello",
        description="Print a greeting from the RSHX Plugin Framework.",
        usage="hello",
        examples="hello",
        notes="Demonstrates that plugin commands work.",
    )

    api.register_help(
        command="greet",
        description="Greet a named person.",
        usage="greet <name>",
        examples="greet Raghav\n  greet World",
        notes="Name defaults to 'World' when not provided.",
    )


def shutdown() -> None:
    """Called when the shell exits."""
    pass


def _cmd_hello(args: list[str], shell_state: "ShellState") -> None:
    _api.print_success("Hello from the RSHX Plugin Framework!")
    _api.print_info(f"  Shell cwd: {shell_state.cwd}")


def _cmd_greet(args: list[str], shell_state: "ShellState") -> None:
    name = args[0] if args else "World"
    _api.print_success(f"Hello, {name}! Greetings from RSHX.")
