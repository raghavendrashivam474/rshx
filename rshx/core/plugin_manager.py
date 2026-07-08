"""
plugin_manager.py
-----------------
Manages the complete lifecycle of every plugin.

Responsibilities
----------------
- Discover plugins on startup.
- Load and validate each plugin.
- Initialise plugins via the Plugin API.
- Enable and disable plugins at runtime.
- Reload plugins on request.
- Shut down all plugins cleanly on exit.

No other module loads plugins directly. All plugin interaction
passes through the Plugin Manager.
"""

from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

from rshx.core.plugin_loader import (
    discover_plugins,
    load_plugin,
    LoadedPlugin,
    PLUGINS_DIR,
)
from rshx.core.plugin_api import PluginAPI
from rshx.core.plugin_registry import PluginRegistry
from rshx.utils.display import print_error, print_info, print_warning

if TYPE_CHECKING:
    from rshx.core.config import ConfigManager


class PluginManager:
    """
    Manages the lifecycle of all RSHX plugins.

    Parameters
    ----------
    registry : PluginRegistry
        The shell's command registry.
    config_manager : ConfigManager
        The shell's configuration manager.
    plugins_dir : Path
        Directory to scan for plugins.
    """

    def __init__(
        self,
        registry: PluginRegistry,
        config_manager: "ConfigManager",
        plugins_dir: Path = PLUGINS_DIR,
    ) -> None:
        self._registry = registry
        self._config_manager = config_manager
        self._plugins_dir = plugins_dir
        self._loaded: dict[str, LoadedPlugin] = {}
        self._apis: dict[str, PluginAPI] = {}

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------

    def discover_and_load_all(self) -> None:
        """
        Discover and load all plugins from the plugins directory.

        Called once during shell startup. Failures in individual
        plugins are logged and skipped without crashing the shell.
        """
        plugin_dirs = discover_plugins(self._plugins_dir)

        for plugin_dir in plugin_dirs:
            self._load_single(plugin_dir)

    def _load_single(self, plugin_dir: Path) -> bool:
        """
        Load, validate, and initialise a single plugin.

        Parameters
        ----------
        plugin_dir : Path
            The plugin directory to load.

        Returns
        -------
        bool
            True if the plugin loaded successfully.
        """
        loaded = load_plugin(plugin_dir)

        if loaded is None:
            print_warning(
                f"Plugin in '{plugin_dir.name}' failed validation and was skipped."
            )
            return False

        name = loaded.manifest.name

        if name in self._loaded:
            print_warning(f"Plugin '{name}' is already loaded. Skipping duplicate.")
            return False

        # Check if plugin is disabled in config
        plugin_cfg = self._get_plugin_config(name)
        if not plugin_cfg.get("enabled", True):
            loaded.enabled = False
            self._loaded[name] = loaded
            return True

        # Create API and initialise
        api = PluginAPI(
            plugin_name=name,
            registry=self._registry,
            config_manager=self._config_manager,
        )

        try:
            loaded.module.initialise(api)
            self._loaded[name] = loaded
            self._apis[name] = api
            return True
        except Exception as exc:
            print_error(f"Plugin '{name}' failed to initialise: {exc}")
            return False

    # ------------------------------------------------------------------
    # Enable / Disable
    # ------------------------------------------------------------------

    def enable(self, name: str) -> bool:
        """
        Enable a loaded but disabled plugin.

        Parameters
        ----------
        name : str
            Plugin name to enable.

        Returns
        -------
        bool
            True if enabled successfully.
        """
        loaded = self._loaded.get(name)
        if loaded is None:
            return False

        if loaded.enabled:
            return True

        api = PluginAPI(
            plugin_name=name,
            registry=self._registry,
            config_manager=self._config_manager,
        )

        try:
            loaded.module.initialise(api)
            loaded.enabled = True
            self._apis[name] = api
            return True
        except Exception as exc:
            print_error(f"Plugin '{name}' failed to enable: {exc}")
            return False

    def disable(self, name: str) -> bool:
        """
        Disable an active plugin.

        Removes all commands registered by the plugin.

        Parameters
        ----------
        name : str
            Plugin name to disable.

        Returns
        -------
        bool
            True if disabled successfully.
        """
        loaded = self._loaded.get(name)
        if loaded is None:
            return False

        if not loaded.enabled:
            return True

        self._registry.unregister_plugin(name)
        loaded.enabled = False
        self._apis.pop(name, None)

        if hasattr(loaded.module, "shutdown"):
            try:
                loaded.module.shutdown()
            except Exception:
                pass

        return True

    # ------------------------------------------------------------------
    # Reload
    # ------------------------------------------------------------------

    def reload(self, name: str) -> bool:
        """
        Reload a plugin by disabling, reloading the module, and re-enabling.

        Parameters
        ----------
        name : str
            Plugin name to reload.

        Returns
        -------
        bool
            True if reloaded successfully.
        """
        loaded = self._loaded.get(name)
        if loaded is None:
            return False

        self.disable(name)
        self._loaded.pop(name, None)

        return self._load_single(loaded.plugin_dir)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def shutdown_all(self) -> None:
        """
        Call shutdown on all active plugins.

        Called when the shell exits. Failures are silently ignored
        to ensure the shell always exits cleanly.
        """
        for name, loaded in self._loaded.items():
            if loaded.enabled and hasattr(loaded.module, "shutdown"):
                try:
                    loaded.module.shutdown()
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def list_plugins(self) -> list[dict]:
        """
        Return a list of plugin info dicts for display.

        Returns
        -------
        list[dict]
            Each dict contains name, version, description, enabled.
        """
        result = []
        for name, loaded in sorted(self._loaded.items()):
            result.append({
                "name": loaded.manifest.name,
                "version": loaded.manifest.version,
                "description": loaded.manifest.description,
                "author": loaded.manifest.author,
                "commands": loaded.manifest.commands,
                "enabled": loaded.enabled,
            })
        return result

    def get_plugin_info(self, name: str) -> dict | None:
        """Return info dict for a specific plugin or None."""
        loaded = self._loaded.get(name)
        if loaded is None:
            return None
        return {
            "name": loaded.manifest.name,
            "version": loaded.manifest.version,
            "description": loaded.manifest.description,
            "author": loaded.manifest.author,
            "commands": loaded.manifest.commands,
            "enabled": loaded.enabled,
            "min_rshx_version": loaded.manifest.min_rshx_version,
        }

    def is_loaded(self, name: str) -> bool:
        """Return True when a plugin is loaded."""
        return name in self._loaded

    def is_enabled(self, name: str) -> bool:
        """Return True when a plugin is loaded and enabled."""
        loaded = self._loaded.get(name)
        return loaded is not None and loaded.enabled

    def count(self) -> int:
        """Return total number of loaded plugins."""
        return len(self._loaded)

    def get_api(self, name: str) -> PluginAPI | None:
        """Return the API instance for a plugin or None."""
        return self._apis.get(name)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_plugin_config(self, name: str) -> dict:
        """Return config dict for a specific plugin."""
        plugins_cfg = getattr(self._config_manager.config, "plugins", {})
        return dict(plugins_cfg.get(name, {}))
