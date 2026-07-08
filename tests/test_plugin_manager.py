"""
test_plugin_manager.py
Unit tests for rshx.core.plugin_manager.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rshx.core.plugin_manager import PluginManager
from rshx.core.plugin_registry import PluginRegistry
from rshx.core.config import ConfigManager


VALID_MANIFEST = '''
name = "test_plugin"
version = "1.0.0"
description = "Test plugin"
author = "Tester"
commands = ["test_cmd"]
'''

VALID_CODE = '''
_api = None

def initialise(api):
    global _api
    _api = api
    api.register_command("test_cmd", _handler, "A test command")

def shutdown():
    pass

def _handler(args, shell_state):
    pass
'''

BROKEN_INIT_CODE = '''
def initialise(api):
    raise RuntimeError("init failed")
'''

NO_INITIALISE_CODE = '''
x = 1
'''


def make_plugin(plugins_dir: Path, name: str, manifest: str, code: str) -> Path:
    d = plugins_dir / name
    d.mkdir(parents=True)
    (d / "manifest.toml").write_text(manifest, encoding="utf-8")
    (d / "plugin.py").write_text(code, encoding="utf-8")
    return d


@pytest.fixture()
def plugins_dir(tmp_path: Path) -> Path:
    d = tmp_path / "plugins"
    d.mkdir()
    return d


@pytest.fixture()
def cfg(tmp_path: Path) -> ConfigManager:
    c = ConfigManager(config_file=tmp_path / "config.toml")
    c.load()
    return c


@pytest.fixture()
def registry() -> PluginRegistry:
    return PluginRegistry()


@pytest.fixture()
def manager(registry, cfg, plugins_dir) -> PluginManager:
    return PluginManager(
        registry=registry,
        config_manager=cfg,
        plugins_dir=plugins_dir,
    )


class TestPluginManagerDiscoverAndLoad:
    def test_loads_valid_plugin(self, manager, plugins_dir, registry):
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        assert manager.is_loaded("test_plugin")
        assert manager.is_enabled("test_plugin")
        assert registry.has("test_cmd")

    def test_skips_invalid_plugin(self, manager, plugins_dir, capsys):
        d = plugins_dir / "bad"
        d.mkdir()
        (d / "manifest.toml").write_text("broken][", encoding="utf-8")
        (d / "plugin.py").write_text(VALID_CODE, encoding="utf-8")
        manager.discover_and_load_all()
        assert manager.count() == 0

    def test_skips_duplicate_plugin_name(self, manager, plugins_dir, capsys):
        make_plugin(plugins_dir, "plugin_a", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        make_plugin(plugins_dir, "plugin_b", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        assert manager.count() == 1

    def test_handles_broken_initialise_gracefully(self, manager, plugins_dir, capsys):
        manifest = VALID_MANIFEST.replace('name = "test_plugin"', 'name = "broken"')
        make_plugin(plugins_dir, "broken", manifest, BROKEN_INIT_CODE)
        manager.discover_and_load_all()
        assert not manager.is_loaded("broken")
        assert "Error" in capsys.readouterr().out

    def test_loads_disabled_plugin_without_initialising(self, manager, plugins_dir, cfg):
        cfg.set_plugin_config("test_plugin", "enabled", False)
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        assert manager.is_loaded("test_plugin")
        assert not manager.is_enabled("test_plugin")

    def test_skips_plugin_with_no_initialise(self, manager, plugins_dir, capsys):
        """Covers plugin_loader.py line 255 - validate_plugin_module returns False."""
        manifest = VALID_MANIFEST.replace('name = "test_plugin"', 'name = "noinit"')
        make_plugin(plugins_dir, "noinit", manifest, NO_INITIALISE_CODE)
        manager.discover_and_load_all()
        assert not manager.is_loaded("noinit")


class TestPluginManagerEnableDisable:
    def test_disable_removes_commands(self, manager, plugins_dir, registry):
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        assert registry.has("test_cmd")
        manager.disable("test_plugin")
        assert not registry.has("test_cmd")
        assert not manager.is_enabled("test_plugin")

    def test_enable_re_registers_commands(self, manager, plugins_dir, registry):
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        manager.disable("test_plugin")
        manager.enable("test_plugin")
        assert registry.has("test_cmd")
        assert manager.is_enabled("test_plugin")

    def test_enable_nonexistent_returns_false(self, manager):
        assert manager.enable("nonexistent") is False

    def test_disable_nonexistent_returns_false(self, manager):
        assert manager.disable("nonexistent") is False

    def test_disable_already_disabled_returns_true(self, manager, plugins_dir, cfg):
        cfg.set_plugin_config("test_plugin", "enabled", False)
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        assert manager.disable("test_plugin") is True

    def test_enable_already_enabled_returns_true(self, manager, plugins_dir):
        """Covers plugin_manager.py line 153 - loaded.enabled is True early return."""
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        assert manager.enable("test_plugin") is True

    def test_enable_with_broken_initialise_returns_false(self, manager, plugins_dir, cfg, capsys):
        """Covers plugin_manager.py lines 166-168 - enable exception handler."""
        cfg.set_plugin_config("test_plugin", "enabled", False)
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, BROKEN_INIT_CODE)
        manager.discover_and_load_all()
        result = manager.enable("test_plugin")
        assert result is False
        assert "Error" in capsys.readouterr().out


class TestPluginManagerReload:
    def test_reload_reloads_plugin(self, manager, plugins_dir, registry):
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        result = manager.reload("test_plugin")
        assert result is True
        assert manager.is_enabled("test_plugin")

    def test_reload_nonexistent_returns_false(self, manager):
        assert manager.reload("nonexistent") is False


class TestPluginManagerShutdown:
    def test_shutdown_all_calls_shutdown_hook(self, manager, plugins_dir):
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        manager.shutdown_all()

    def test_shutdown_handles_exception_gracefully(self, manager, plugins_dir):
        """Covers plugin_manager.py lines 200-201 - shutdown exception handler."""
        broken_shutdown = VALID_CODE + "\ndef shutdown():\n    raise RuntimeError('shutdown failed')\n"
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, broken_shutdown)
        manager.discover_and_load_all()
        manager.shutdown_all()


class TestPluginManagerQuery:
    def test_list_plugins_empty(self, manager):
        assert manager.list_plugins() == []

    def test_list_plugins_shows_loaded(self, manager, plugins_dir):
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        result = manager.list_plugins()
        assert len(result) == 1
        assert result[0]["name"] == "test_plugin"

    def test_get_plugin_info_returns_dict(self, manager, plugins_dir):
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        info = manager.get_plugin_info("test_plugin")
        assert info is not None
        assert info["name"] == "test_plugin"
        assert "version" in info
        assert "enabled" in info

    def test_get_plugin_info_returns_none_for_missing(self, manager):
        assert manager.get_plugin_info("nonexistent") is None

    def test_get_api_returns_api(self, manager, plugins_dir):
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        api = manager.get_api("test_plugin")
        assert api is not None

    def test_get_api_returns_none_for_disabled(self, manager, plugins_dir, cfg):
        cfg.set_plugin_config("test_plugin", "enabled", False)
        make_plugin(plugins_dir, "test_plugin", VALID_MANIFEST, VALID_CODE)
        manager.discover_and_load_all()
        assert manager.get_api("test_plugin") is None
