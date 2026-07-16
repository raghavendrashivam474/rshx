"""
plugin_manager.py
-----------------
Manages the complete lifecycle of every plugin.
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
    """Manages the lifecycle of all RSHX plugins."""

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

    def discover_and_load_all(self) -> None:
        """Discover and load all plugins from the plugins directory."""
        plugin_dirs = discover_plugins(self._plugins_dir)
        for plugin_dir in plugin_dirs:
            self._load_single(plugin_dir)

    def _load_single(self, plugin_dir: Path) -> bool:
        """Load, validate, and initialise a single plugin."""
        loaded = load_plugin(plugin_dir)

        if loaded is None:
            print_warning(
                f"Plugin '{plugin_dir.name}' failed validation and was skipped.\n"
                f"  Check that manifest.toml is valid TOML without BOM\n"
                f"  and that plugin.py defines an initialise(api) function."
            )
            return False

        name = loaded.manifest.name

        if name in self._loaded:
            print_warning(
                f"Plugin '{name}' is already loaded. "
                f"Duplicate in '{plugin_dir.name}' was skipped."
            )
            return False

        plugin_cfg = self._get_plugin_config(name)
        if not plugin_cfg.get("enabled", True):
            loaded.enabled = False
            self._loaded[name] = loaded
            return True

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
            print_error(
                f"Plugin '{name}' failed to initialise: {exc}\n"
                f"  The plugin has been skipped. Fix the error in plugin.py\n"
                f"  and reload with: plugin reload {name}"
            )
            return False

    def enable(self, name: str) -> bool:
        """Enable a loaded but disabled plugin."""
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
            print_error(
                f"Plugin '{name}' failed to enable: {exc}\n"
                f"  Fix the error in plugin.py and try again."
            )
            return False

    def disable(self, name: str) -> bool:
        """Disable an active plugin."""
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

    def reload(self, name: str) -> bool:
        """Reload a plugin."""
        loaded = self._loaded.get(name)
        if loaded is None:
            return False

        self.disable(name)
        self._loaded.pop(name, None)
        return self._load_single(loaded.plugin_dir)

    def shutdown_all(self) -> None:
        """Call shutdown on all active plugins."""
        for name, loaded in self._loaded.items():
            if loaded.enabled and hasattr(loaded.module, "shutdown"):
                try:
                    loaded.module.shutdown()
                except Exception:
                    pass

    def list_plugins(self) -> list[dict]:
        """Return a list of plugin info dicts."""
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
        return name in self._loaded

    def is_enabled(self, name: str) -> bool:
        loaded = self._loaded.get(name)
        return loaded is not None and loaded.enabled

    def count(self) -> int:
        return len(self._loaded)

    def get_api(self, name: str) -> PluginAPI | None:
        return self._apis.get(name)

    def _get_plugin_config(self, name: str) -> dict:
        plugins_cfg = getattr(self._config_manager.config, "plugins", {})
        return dict(plugins_cfg.get(name, {}))
