"""
plugin_registry.py
------------------
Maintains the registry of all commands provided by plugins.

The executor queries this registry after checking built-ins and
before falling back to external system commands.

Responsibilities
----------------
- Register plugin commands.
- Detect and reject duplicate command names.
- Look up commands by name.
- List all registered plugin commands.
- Remove commands when a plugin is disabled.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rshx.core.repl import ShellState


@dataclass
class PluginCommand:
    """
    A single command registered by a plugin.

    Attributes
    ----------
    name : str
        The command name.
    handler : Callable
        The function invoked when the command is executed.
    plugin_name : str
        The name of the plugin that registered this command.
    description : str
        Short description for display in listings.
    """
    name: str
    handler: Callable
    plugin_name: str
    description: str = ""


class PluginRegistry:
    """
    Registry of all plugin-provided commands.

    The registry is the single point of truth for plugin commands.
    No other module maintains a list of plugin commands.
    """

    def __init__(self) -> None:
        self._commands: dict[str, PluginCommand] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        handler: Callable,
        plugin_name: str,
        description: str = "",
    ) -> bool:
        """
        Register a plugin command.

        Parameters
        ----------
        name : str
            Command name. Must not conflict with existing registrations.
        handler : Callable
            Function to call when the command is invoked.
        plugin_name : str
            Name of the owning plugin.
        description : str
            Short description.

        Returns
        -------
        bool
            True if registered. False if the name already exists.
        """
        if name in self._commands:
            return False

        self._commands[name] = PluginCommand(
            name=name,
            handler=handler,
            plugin_name=plugin_name,
            description=description,
        )
        return True

    def unregister_plugin(self, plugin_name: str) -> list[str]:
        """
        Remove all commands registered by a specific plugin.

        Parameters
        ----------
        plugin_name : str
            Name of the plugin whose commands should be removed.

        Returns
        -------
        list[str]
            Names of commands that were removed.
        """
        to_remove = [
            name for name, cmd in self._commands.items()
            if cmd.plugin_name == plugin_name
        ]
        for name in to_remove:
            del self._commands[name]
        return to_remove

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> PluginCommand | None:
        """
        Look up a command by name.

        Parameters
        ----------
        name : str
            The command name to look up.

        Returns
        -------
        PluginCommand | None
            The command if found, None otherwise.
        """
        return self._commands.get(name)

    def has(self, name: str) -> bool:
        """Return True when the command name is registered."""
        return name in self._commands

    def all(self) -> dict[str, PluginCommand]:
        """Return a copy of all registered commands."""
        return dict(self._commands)

    def commands_for_plugin(self, plugin_name: str) -> list[str]:
        """Return command names registered by a specific plugin."""
        return [
            name for name, cmd in self._commands.items()
            if cmd.plugin_name == plugin_name
        ]

    def count(self) -> int:
        """Return the number of registered plugin commands."""
        return len(self._commands)

    def dispatch(
        self,
        name: str,
        args: list[str],
        shell_state: "ShellState",
    ) -> bool:
        """
        Execute a plugin command if it exists.

        Parameters
        ----------
        name : str
            The command name to execute.
        args : list[str]
            Arguments to pass to the handler.
        shell_state : ShellState
            Current shell state.

        Returns
        -------
        bool
            True if the command was found and executed.
            False if no command with that name is registered.
        """
        cmd = self._commands.get(name)
        if cmd is None:
            return False

        try:
            cmd.handler(args, shell_state)
        except Exception as exc:
            from rshx.utils.display import print_error
            print_error(
                f"Plugin command '{name}' raised an error: {exc}"
            )
        return True
