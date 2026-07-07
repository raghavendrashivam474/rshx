"""
config.py
---------
Centralized configuration management for RSHX.

Responsibilities
----------------
- Define the configuration file location.
- Generate default configuration.
- Load configuration from TOML file.
- Save configuration to TOML file.
- Validate configuration values.
- Recover from missing or corrupted files.
- Provide typed access to all configuration sections.

The Configuration Manager is the single source of truth for all
persistent shell settings. No other module reads or writes the
configuration file directly.

Configuration file location
---------------------------
~/.rshx/config.toml
"""

from __future__ import annotations
import tomllib
import tomli_w
from pathlib import Path
from dataclasses import dataclass, field

from rshx.core.theme import is_valid_theme, DEFAULT_THEME_NAME


# ---------------------------------------------------------------------------
# File location
# ---------------------------------------------------------------------------

CONFIG_DIR: Path = Path.home() / ".rshx"
CONFIG_FILE: Path = CONFIG_DIR / "config.toml"


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------

@dataclass
class RshxConfig:
    """
    Typed representation of all RSHX configuration.

    Attributes
    ----------
    version : str
        Configuration schema version.
    theme : str
        Active theme name.
    show_cwd : bool
        Show current directory in prompt.
    show_git_branch : bool
        Show git branch in prompt.
    aliases : dict[str, str]
        Persistent alias definitions.
    environment : dict[str, str]
        Persistent environment variable definitions.
    startup_commands : list[str]
        Commands executed automatically on shell startup.
    """
    version: str = "0.5.0"
    theme: str = DEFAULT_THEME_NAME
    show_cwd: bool = True
    show_git_branch: bool = False
    aliases: dict[str, str] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
    startup_commands: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Configuration Manager
# ---------------------------------------------------------------------------

class ConfigManager:
    """
    Manages loading, saving, and validating RSHX configuration.

    Parameters
    ----------
    config_file : Path
        Path to the TOML configuration file.
        Defaults to ~/.rshx/config.toml.
    """

    def __init__(self, config_file: Path = CONFIG_FILE) -> None:
        self._config_file = config_file
        self._config: RshxConfig = RshxConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def config(self) -> RshxConfig:
        """Return the current configuration."""
        return self._config

    def load(self) -> None:
        """
        Load configuration from the TOML file.

        Creates default configuration if the file does not exist.
        Falls back to defaults if the file is corrupted or invalid.
        Always succeeds - the shell never fails to start due to
        a bad configuration file.
        """
        if not self._config_file.exists():
            self._config = RshxConfig()
            self.save()
            return

        try:
            raw = self._config_file.read_text(encoding="utf-8")
            data = tomllib.loads(raw)
            self._config = self._parse(data)
        except (tomllib.TOMLDecodeError, Exception):
            # Corrupted file - back it up and use defaults
            self._backup_corrupted()
            self._config = RshxConfig()
            self.save()

    def save(self) -> None:
        """
        Save current configuration to the TOML file.

        Creates the configuration directory if it does not exist.
        Silently ignores write failures to avoid crashing the shell.
        """
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            data = self._serialise()
            self._config_file.write_bytes(tomli_w.dumps(data).encode("utf-8"))
        except OSError:
            pass

    def set_theme(self, theme_name: str) -> bool:
        """
        Set the active theme.

        Parameters
        ----------
        theme_name : str
            Theme name to activate.

        Returns
        -------
        bool
            True if the theme was set, False if the name is invalid.
        """
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
        """
        Update prompt display options.

        Parameters
        ----------
        show_cwd : bool | None
            If provided, sets whether cwd is shown.
        show_git_branch : bool | None
            If provided, sets whether git branch is shown.
        """
        if show_cwd is not None:
            self._config.show_cwd = show_cwd
        if show_git_branch is not None:
            self._config.show_git_branch = show_git_branch
        self.save()

    def save_alias(self, name: str, value: str) -> None:
        """Persist an alias to configuration."""
        self._config.aliases[name] = value
        self.save()

    def delete_alias(self, name: str) -> None:
        """Remove an alias from configuration."""
        self._config.aliases.pop(name, None)
        self.save()

    def save_variable(self, name: str, value: str) -> None:
        """Persist an environment variable to configuration."""
        self._config.environment[name] = value
        self.save()

    def delete_variable(self, name: str) -> None:
        """Remove an environment variable from configuration."""
        self._config.environment.pop(name, None)
        self.save()

    def add_startup_command(self, command: str) -> None:
        """Append a startup command."""
        if command not in self._config.startup_commands:
            self._config.startup_commands.append(command)
            self.save()

    def remove_startup_command(self, command: str) -> None:
        """Remove a startup command if present."""
        if command in self._config.startup_commands:
            self._config.startup_commands.remove(command)
            self.save()

    def validate(self) -> list[str]:
        """
        Validate the current configuration.

        Returns
        -------
        list[str]
            A list of validation error messages. Empty means valid.
        """
        errors: list[str] = []

        if not is_valid_theme(self._config.theme):
            errors.append(
                f"Invalid theme '{self._config.theme}'. "
                f"Resetting to default."
            )
            self._config.theme = DEFAULT_THEME_NAME

        return errors

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse(self, data: dict) -> RshxConfig:
        """Parse raw TOML dict into RshxConfig."""
        general = data.get("general", {})
        prompt = data.get("prompt", {})

        config = RshxConfig(
            version=str(general.get("version", "0.5.0")),
            theme=str(general.get("theme", DEFAULT_THEME_NAME)),
            show_cwd=bool(prompt.get("show_cwd", True)),
            show_git_branch=bool(prompt.get("show_git_branch", False)),
            aliases=dict(data.get("aliases", {})),
            environment=dict(data.get("environment", {})),
            startup_commands=list(data.get("startup", {}).get("commands", [])),
        )

        return config

    def _serialise(self) -> dict:
        """Serialise RshxConfig to a TOML-compatible dict."""
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
        }

    def _backup_corrupted(self) -> None:
        """Rename corrupted config file to config.toml.bak."""
        try:
            backup = self._config_file.with_suffix(".toml.bak")
            self._config_file.rename(backup)
        except OSError:
            pass
