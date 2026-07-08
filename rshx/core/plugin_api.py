"""
plugin_api.py
-------------
The Plugin API is the only interface through which plugins may
interact with the RSHX shell.

Plugins must never import from rshx.core directly. They must
communicate exclusively through the PluginAPI object passed to
them during initialisation.

This boundary means the core shell internals can change without
breaking plugins, as long as the API contract is maintained.

Responsibilities
----------------
- Register commands with the registry.
- Register help entries visible in the help system.
- Register completions for plugin commands.
- Access shell configuration safely.
- Display formatted output using shell display utilities.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from rshx.core.plugin_registry import PluginRegistry
    from rshx.core.repl import ShellState
    from rshx.core.config import ConfigManager


class PluginAPI:
    """
    Safe interface between plugins and the RSHX shell.

    Parameters
    ----------
    plugin_name : str
        The name of the plugin that owns this API instance.
    registry : PluginRegistry
        The shell's command registry.
    config_manager : ConfigManager
        The shell's configuration manager.
    """

    def __init__(
        self,
        plugin_name: str,
        registry: "PluginRegistry",
        config_manager: "ConfigManager",
    ) -> None:
        self._plugin_name = plugin_name
        self._registry = registry
        self._config_manager = config_manager
        self._help_entries: dict[str, dict[str, str]] = {}

    # ------------------------------------------------------------------
    # Command registration
    # ------------------------------------------------------------------

    def register_command(
        self,
        name: str,
        handler: Callable,
        description: str = "",
    ) -> bool:
        """
        Register a command provided by this plugin.

        Parameters
        ----------
        name : str
            The command name users will type.
        handler : Callable
            Function called when the command is invoked.
            Signature: handler(args: list[str], shell_state: ShellState)
        description : str
            Short description shown in help output.

        Returns
        -------
        bool
            True if registered successfully, False if name conflicts.
        """
        return self._registry.register(
            name=name,
            handler=handler,
            plugin_name=self._plugin_name,
            description=description,
        )

    # ------------------------------------------------------------------
    # Help registration
    # ------------------------------------------------------------------

    def register_help(
        self,
        command: str,
        description: str,
        usage: str,
        examples: str,
        notes: str = "",
    ) -> None:
        """
        Register detailed help for a plugin command.

        Parameters
        ----------
        command : str
            The command name to attach help to.
        description : str
            Short description of the command.
        usage : str
            Usage syntax string.
        examples : str
            Newline-separated example invocations.
        notes : str
            Optional additional notes.
        """
        self._help_entries[command] = {
            "description": description,
            "usage": usage,
            "examples": examples,
            "notes": notes,
        }

    def get_help_entries(self) -> dict[str, dict[str, str]]:
        """Return all registered help entries for this plugin."""
        return dict(self._help_entries)

    # ------------------------------------------------------------------
    # Configuration access
    # ------------------------------------------------------------------

    def get_config(self) -> dict:
        """
        Return this plugin's configuration section.

        Returns a copy of the plugin-specific config dict.
        Plugins receive only their own configuration.

        Returns
        -------
        dict
            Plugin configuration key-value pairs.
        """
        all_cfg = self._config_manager.config
        plugins_cfg = getattr(all_cfg, "plugins", {})
        return dict(plugins_cfg.get(self._plugin_name, {}))

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def print_output(self, message: str) -> None:
        """Print standard output."""
        from rshx.utils.display import print_output
        print_output(message)

    def print_success(self, message: str) -> None:
        """Print a success message."""
        from rshx.utils.display import print_success
        print_success(message)

    def print_error(self, message: str) -> None:
        """Print an error message."""
        from rshx.utils.display import print_error
        print_error(message)

    def print_info(self, message: str) -> None:
        """Print an informational message."""
        from rshx.utils.display import print_info
        print_info(message)

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        from rshx.utils.display import print_warning
        print_warning(message)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def plugin_name(self) -> str:
        """Return the name of the owning plugin."""
        return self._plugin_name
