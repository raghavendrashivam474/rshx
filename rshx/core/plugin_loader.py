"""
plugin_loader.py
----------------
Responsible for discovering, loading, and validating plugins.

Discovery scans the rshx/plugins/ directory for subdirectories
containing a manifest.toml and plugin.py.

Validation checks that all required manifest fields are present
and that the plugin module exposes the required interface.

Loading uses importlib to dynamically import plugin modules
without hardcoding plugin names in the shell core.

Responsibilities
----------------
- Scan the plugins directory.
- Load manifest.toml for each plugin.
- Validate manifest structure.
- Dynamically import plugin modules.
- Validate plugin module interface.
- Return loaded plugin objects.
"""

from __future__ import annotations
import importlib
import importlib.util
import tomllib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Plugin manifest
# ---------------------------------------------------------------------------

REQUIRED_MANIFEST_FIELDS = {
    "name", "version", "description", "author", "commands",
}

PLUGINS_DIR: Path = Path(__file__).parent.parent / "plugins"


@dataclass
class PluginManifest:
    """
    Metadata loaded from a plugin's manifest.toml.

    Attributes
    ----------
    name : str
        Unique plugin identifier.
    version : str
        Plugin version string.
    description : str
        Human-readable description.
    author : str
        Plugin author name.
    commands : list[str]
        Command names this plugin registers.
    min_rshx_version : str
        Minimum RSHX version required.
    """
    name: str
    version: str
    description: str
    author: str
    commands: list[str] = field(default_factory=list)
    min_rshx_version: str = "0.1.0"


@dataclass
class LoadedPlugin:
    """
    A successfully loaded plugin ready for registration.

    Attributes
    ----------
    manifest : PluginManifest
        Plugin metadata.
    module : Any
        The imported Python module.
    plugin_dir : Path
        Directory where the plugin lives.
    enabled : bool
        Whether the plugin is currently active.
    """
    manifest: PluginManifest
    module: Any
    plugin_dir: Path
    enabled: bool = True


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover_plugins(plugins_dir: Path = PLUGINS_DIR) -> list[Path]:
    """
    Scan the plugins directory for valid plugin directories.

    A valid plugin directory contains both manifest.toml and plugin.py.

    Parameters
    ----------
    plugins_dir : Path
        Directory to scan for plugins.

    Returns
    -------
    list[Path]
        Sorted list of plugin directory paths.
    """
    if not plugins_dir.exists():
        return []

    found = []
    for entry in sorted(plugins_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("_"):
            continue
        if (entry / "manifest.toml").exists() and (entry / "plugin.py").exists():
            found.append(entry)

    return found


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def load_manifest(plugin_dir: Path) -> PluginManifest | None:
    """
    Load and validate a plugin's manifest.toml.

    Parameters
    ----------
    plugin_dir : Path
        The plugin directory containing manifest.toml.

    Returns
    -------
    PluginManifest | None
        Parsed manifest or None if invalid.
    """
    manifest_path = plugin_dir / "manifest.toml"

    try:
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return None

    missing = REQUIRED_MANIFEST_FIELDS - set(data.keys())
    if missing:
        return None

    return PluginManifest(
        name=str(data["name"]),
        version=str(data["version"]),
        description=str(data["description"]),
        author=str(data["author"]),
        commands=list(data.get("commands", [])),
        min_rshx_version=str(data.get("min_rshx_version", "0.1.0")),
    )


# ---------------------------------------------------------------------------
# Module loading
# ---------------------------------------------------------------------------

def load_plugin_module(plugin_dir: Path) -> Any | None:
    """
    Dynamically import a plugin's plugin.py module.

    Parameters
    ----------
    plugin_dir : Path
        The plugin directory containing plugin.py.

    Returns
    -------
    Any | None
        The imported module or None on failure.
    """
    plugin_file = plugin_dir / "plugin.py"
    module_name = f"rshx.plugins.{plugin_dir.name}.plugin"

    try:
        spec = importlib.util.spec_from_file_location(
            module_name,
            plugin_file,
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    except Exception:
        return None


def validate_plugin_module(module: Any) -> bool:
    """
    Validate that a plugin module exposes the required interface.

    A valid plugin module must define:
    - initialise(api: PluginAPI) -> None

    Parameters
    ----------
    module : Any
        The imported plugin module.

    Returns
    -------
    bool
        True if the module is valid.
    """
    return callable(getattr(module, "initialise", None))


# ---------------------------------------------------------------------------
# Full load pipeline
# ---------------------------------------------------------------------------

def load_plugin(plugin_dir: Path) -> LoadedPlugin | None:
    """
    Run the full load pipeline for a single plugin directory.

    Steps: discover -> load manifest -> load module -> validate.

    Parameters
    ----------
    plugin_dir : Path
        Directory containing manifest.toml and plugin.py.

    Returns
    -------
    LoadedPlugin | None
        The loaded plugin or None if any step failed.
    """
    manifest = load_manifest(plugin_dir)
    if manifest is None:
        return None

    module = load_plugin_module(plugin_dir)
    if module is None:
        return None

    if not validate_plugin_module(module):
        return None

    return LoadedPlugin(
        manifest=manifest,
        module=module,
        plugin_dir=plugin_dir,
    )
