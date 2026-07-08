"""
config.py
---------
Centralized configuration management for RSHX.

Sprint 5 addition: plugins section for per-plugin configuration.
"""

from __future__ import annotations
import tomllib
import tomli_w
from pathlib import Path
from dataclasses import dataclass, field

from rshx.core.theme import is_valid_theme, DEFAULT_THEME_NAME


CONFIG_DIR: Path = Path.home() / ".rshx"
CONFIG_FILE: Path = CONFIG_DIR / "config.toml"


@dataclass
class RshxConfig:
    """
    Typed representation of all RSHX configuration.

    Attributes
    ----------
    version : str
    theme : str
    show_cwd : bool
    show_git_branch : bool
    aliases : dict[str, str]
    environment : dict[str, str]
    startup_commands : list[str]
    plugins : dict[str, dict]
        Per-plugin configuration keyed by plugin name.
    """
    version: str = "0.5.0"
    theme: str = DEFAULT_THEME_NAME
    show_cwd: bool = True
    show_git_branch: bool = False
    aliases: dict[str, str] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
    startup_commands: list[str] = field(default_factory=list)
    plugins: dict[str, dict] = field(default_factory=dict)


class ConfigManager:
    """
    Manages loading, saving, and validating RSHX configuration.
    """

    def __init__(self, config_file: Path = CONFIG_FILE) -> None:
        self._config_file = config_file
        self._config: RshxConfig = RshxConfig()

    @property
    def config(self) -> RshxConfig:
        return self._config

    def load(self) -> None:
        if not self._config_file.exists():
            self._config = RshxConfig()
            self.save()
            return

        try:
            raw = self._config_file.read_text(encoding="utf-8")
            data = tomllib.loads(raw)
            self._config = self._parse(data)
        except (tomllib.TOMLDecodeError, Exception):
            self._backup_corrupted()
            self._config = RshxConfig()
            self.save()

    def save(self) -> None:
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            data = self._serialise()
            self._config_file.write_bytes(tomli_w.dumps(data).encode("utf-8"))
        except OSError:
            pass

    def set_theme(self, theme_name: str) -> bool:
        if not is_valid_theme(theme_name):
            return False
        self._config.theme = theme_name
        self.save()
        return True

    def set_prompt_options(
        self,
        show_cwd: bool | None = None,
        show_git_branch: bool | None = None,
    ) -> None:
        if show_cwd is not None:
            self._config.show_cwd = show_cwd
        if show_git_branch is not None:
            self._config.show_git_branch = show_git_branch
        self.save()

    def save_alias(self, name: str, value: str) -> None:
        self._config.aliases[name] = value
        self.save()

    def delete_alias(self, name: str) -> None:
        self._config.aliases.pop(name, None)
        self.save()

    def save_variable(self, name: str, value: str) -> None:
        self._config.environment[name] = value
        self.save()

    def delete_variable(self, name: str) -> None:
        self._config.environment.pop(name, None)
        self.save()

    def add_startup_command(self, command: str) -> None:
        if command not in self._config.startup_commands:
            self._config.startup_commands.append(command)
            self.save()

    def remove_startup_command(self, command: str) -> None:
        if command in self._config.startup_commands:
            self._config.startup_commands.remove(command)
            self.save()

    def set_plugin_config(self, plugin_name: str, key: str, value) -> None:
        """Set a configuration value for a specific plugin."""
        if plugin_name not in self._config.plugins:
            self._config.plugins[plugin_name] = {}
        self._config.plugins[plugin_name][key] = value
        self.save()

    def get_plugin_config(self, plugin_name: str) -> dict:
        """Return configuration dict for a specific plugin."""
        return dict(self._config.plugins.get(plugin_name, {}))

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not is_valid_theme(self._config.theme):
            errors.append(
                f"Invalid theme '{self._config.theme}'. Resetting to default."
            )
            self._config.theme = DEFAULT_THEME_NAME
        return errors

    def _parse(self, data: dict) -> RshxConfig:
        general = data.get("general", {})
        prompt = data.get("prompt", {})
        plugins_raw = data.get("plugins", {})

        plugins: dict[str, dict] = {}
        for pname, pdata in plugins_raw.items():
            if isinstance(pdata, dict):
                plugins[pname] = dict(pdata)

        return RshxConfig(
            version=str(general.get("version", "0.5.0")),
            theme=str(general.get("theme", DEFAULT_THEME_NAME)),
            show_cwd=bool(prompt.get("show_cwd", True)),
            show_git_branch=bool(prompt.get("show_git_branch", False)),
            aliases=dict(data.get("aliases", {})),
            environment=dict(data.get("environment", {})),
            startup_commands=list(data.get("startup", {}).get("commands", [])),
            plugins=plugins,
        )

    def _serialise(self) -> dict:
        return {
            "general": {
                "version": self._config.version,
                "theme": self._config.theme,
            },
            "prompt": {
                "show_cwd": self._config.show_cwd,
                "show_git_branch": self._config.show_git_branch,
            },
            "aliases": dict(self._config.aliases),
            "environment": dict(self._config.environment),
            "startup": {
                "commands": list(self._config.startup_commands),
            },
            "plugins": {
                k: dict(v) for k, v in self._config.plugins.items()
            },
        }

    def _backup_corrupted(self) -> None:
        try:
            backup = self._config_file.with_suffix(".toml.bak")
            self._config_file.rename(backup)
        except OSError:
            pass
