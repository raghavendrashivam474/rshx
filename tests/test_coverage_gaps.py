"""
test_coverage_gaps.py
Targeted tests for the final remaining coverage gaps.
"""

import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rshx.core.config import ConfigManager
from rshx.core.plugin_loader import discover_plugins, load_plugin_module
from rshx.core.plugin_manager import PluginManager
from rshx.core.plugin_registry import PluginRegistry


# ---------------------------------------------------------------------------
# config.py line 157 - return RshxConfig inside isinstance block
# ---------------------------------------------------------------------------

class TestConfigParseWithValidPluginDict:
    def test_load_with_valid_dict_plugin_config_reaches_return(self, tmp_path):
        """
        Covers config.py line 157.
        When at least one plugin entry IS a dict the isinstance branch
        is entered AND the return RshxConfig line is reached.
        """
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            '[general]\nversion = "0.5.0"\ntheme = "default"\n'
            '[prompt]\nshow_cwd = true\nshow_git_branch = false\n'
            '[aliases]\n[environment]\n[startup]\ncommands = []\n'
            '[plugins.myplugin]\nenabled = true\n',
            encoding="utf-8",
        )
        cfg = ConfigManager(config_file=config_file)
        cfg.load()
        assert "myplugin" in cfg.config.plugins
        assert cfg.config.plugins["myplugin"].get("enabled") is True


# ---------------------------------------------------------------------------
# plugin_loader.py line 121 - entry.name.startswith("_") branch
# ---------------------------------------------------------------------------

class TestDiscoverPluginsUnderscoreBranch:
    def test_underscore_directory_is_skipped(self, tmp_path):
        """
        Covers plugin_loader.py line 121.
        A directory starting with _ must be explicitly skipped.
        """
        underscore_dir = tmp_path / "_private"
        underscore_dir.mkdir()
        (underscore_dir / "manifest.toml").write_text(
            'name="x"\nversion="1"\ndescription="x"\nauthor="x"\ncommands=[]\n',
            encoding="utf-8",
        )
        (underscore_dir / "plugin.py").write_text("def initialise(api): pass\n", encoding="utf-8")

        result = discover_plugins(tmp_path)
        names = [p.name for p in result]
        assert "_private" not in names

    def test_non_underscore_directory_is_included(self, tmp_path):
        """Confirm normal directories are still found alongside underscore ones."""
        underscore_dir = tmp_path / "_skip"
        underscore_dir.mkdir()

        normal_dir = tmp_path / "myplugin"
        normal_dir.mkdir()
        (normal_dir / "manifest.toml").write_text(
            'name="x"\nversion="1"\ndescription="x"\nauthor="x"\ncommands=[]\n',
            encoding="utf-8",
        )
        (normal_dir / "plugin.py").write_text("def initialise(api): pass\n", encoding="utf-8")

        result = discover_plugins(tmp_path)
        names = [p.name for p in result]
        assert "myplugin" in names
        assert "_skip" not in names


# ---------------------------------------------------------------------------
# plugin_loader.py line 196 - spec is None branch
# ---------------------------------------------------------------------------

class TestLoadPluginModuleSpecNone:
    def test_returns_none_when_spec_is_none(self, tmp_path):
        """
        Covers plugin_loader.py line 196.
        When spec_from_file_location returns None the function returns None.
        """
        plugin_dir = tmp_path / "myplugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.py").write_text("def initialise(api): pass\n", encoding="utf-8")

        with patch("importlib.util.spec_from_file_location", return_value=None):
            result = load_plugin_module(plugin_dir)

        assert result is None


# ---------------------------------------------------------------------------
# plugin_manager.py lines 200-201 - shutdown exception handler
# ---------------------------------------------------------------------------

VALID_MANIFEST = '''
name = "shutdowntest"
version = "1.0.0"
description = "Test"
author = "Tester"
commands = []
'''

BROKEN_SHUTDOWN_CODE = '''
def initialise(api):
    pass

def shutdown():
    raise RuntimeError("shutdown exploded")
'''


class TestPluginManagerShutdownException:
    def test_shutdown_exception_is_silently_ignored(self, tmp_path):
        """
        Covers plugin_manager.py lines 200-201.
        RuntimeError during shutdown must not propagate.
        """
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        plugin_dir = plugins_dir / "shutdowntest"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.toml").write_text(VALID_MANIFEST, encoding="utf-8")
        (plugin_dir / "plugin.py").write_text(BROKEN_SHUTDOWN_CODE, encoding="utf-8")

        cfg = ConfigManager(config_file=tmp_path / "config.toml")
        cfg.load()
        registry = PluginRegistry()
        manager = PluginManager(
            registry=registry,
            config_manager=cfg,
            plugins_dir=plugins_dir,
        )
        manager.discover_and_load_all()
        assert manager.is_loaded("shutdowntest")

        # shutdown_all must complete without raising
        manager.shutdown_all()


# ---------------------------------------------------------------------------
# Example plugin integration tests
# Covers plugins/hello/plugin.py and plugins/sysinfo/plugin.py
# ---------------------------------------------------------------------------

class TestHelloPlugin:
    def test_hello_plugin_initialises_and_registers_commands(self, tmp_path):
        """Integration test covering hello/plugin.py."""
        from rshx.core.plugin_registry import PluginRegistry
        from rshx.core.config import ConfigManager
        from rshx.core.plugin_api import PluginAPI
        from rshx.plugins.hello import plugin as hello_plugin

        cfg = ConfigManager(config_file=tmp_path / "config.toml")
        cfg.load()
        registry = PluginRegistry()
        api = PluginAPI("hello", registry, cfg)

        hello_plugin.initialise(api)

        assert registry.has("hello")
        assert registry.has("greet")

    def test_hello_command_executes(self, tmp_path, capsys):
        from rshx.core.plugin_registry import PluginRegistry
        from rshx.core.config import ConfigManager
        from rshx.core.plugin_api import PluginAPI
        from rshx.core.repl import ShellState
        from rshx.plugins.hello import plugin as hello_plugin

        cfg = ConfigManager(config_file=tmp_path / "config.toml")
        cfg.load()
        registry = PluginRegistry()
        api = PluginAPI("hello", registry, cfg)
        hello_plugin.initialise(api)

        state = ShellState(cwd=tmp_path)
        registry.dispatch("hello", [], state)
        captured = capsys.readouterr()
        assert "Hello" in captured.out

    def test_greet_command_with_name(self, tmp_path, capsys):
        from rshx.core.plugin_registry import PluginRegistry
        from rshx.core.config import ConfigManager
        from rshx.core.plugin_api import PluginAPI
        from rshx.core.repl import ShellState
        from rshx.plugins.hello import plugin as hello_plugin

        cfg = ConfigManager(config_file=tmp_path / "config.toml")
        cfg.load()
        registry = PluginRegistry()
        api = PluginAPI("hello", registry, cfg)
        hello_plugin.initialise(api)

        state = ShellState(cwd=tmp_path)
        registry.dispatch("greet", ["Raghav"], state)
        captured = capsys.readouterr()
        assert "Raghav" in captured.out

    def test_hello_plugin_shutdown(self, tmp_path):
        from rshx.plugins.hello import plugin as hello_plugin
        hello_plugin.shutdown()


class TestSysinfoPlugin:
    def test_sysinfo_plugin_initialises_and_registers_commands(self, tmp_path):
        """Integration test covering sysinfo/plugin.py."""
        from rshx.core.plugin_registry import PluginRegistry
        from rshx.core.config import ConfigManager
        from rshx.core.plugin_api import PluginAPI
        from rshx.plugins.sysinfo import plugin as sysinfo_plugin

        cfg = ConfigManager(config_file=tmp_path / "config.toml")
        cfg.load()
        registry = PluginRegistry()
        api = PluginAPI("sysinfo", registry, cfg)

        sysinfo_plugin.initialise(api)

        assert registry.has("sysinfo")
        assert registry.has("uptime")

    def test_sysinfo_command_executes(self, tmp_path, capsys):
        from rshx.core.plugin_registry import PluginRegistry
        from rshx.core.config import ConfigManager
        from rshx.core.plugin_api import PluginAPI
        from rshx.core.repl import ShellState
        from rshx.plugins.sysinfo import plugin as sysinfo_plugin

        cfg = ConfigManager(config_file=tmp_path / "config.toml")
        cfg.load()
        registry = PluginRegistry()
        api = PluginAPI("sysinfo", registry, cfg)
        sysinfo_plugin.initialise(api)

        state = ShellState(cwd=tmp_path)
        registry.dispatch("sysinfo", [], state)
        captured = capsys.readouterr()
        assert "System" in captured.out or "OS" in captured.out

    def test_uptime_command_executes(self, tmp_path, capsys):
        from rshx.core.plugin_registry import PluginRegistry
        from rshx.core.config import ConfigManager
        from rshx.core.plugin_api import PluginAPI
        from rshx.core.repl import ShellState
        from rshx.plugins.sysinfo import plugin as sysinfo_plugin

        cfg = ConfigManager(config_file=tmp_path / "config.toml")
        cfg.load()
        registry = PluginRegistry()
        api = PluginAPI("sysinfo", registry, cfg)
        sysinfo_plugin.initialise(api)

        state = ShellState(cwd=tmp_path)
        registry.dispatch("uptime", [], state)

    def test_sysinfo_plugin_shutdown(self, tmp_path):
        from rshx.plugins.sysinfo import plugin as sysinfo_plugin
        sysinfo_plugin.shutdown()
