"""
test_plugin_api.py
Unit tests for rshx.core.plugin_api.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rshx.core.plugin_api import PluginAPI
from rshx.core.plugin_registry import PluginRegistry
from rshx.core.config import ConfigManager


@pytest.fixture()
def registry() -> PluginRegistry:
    return PluginRegistry()


@pytest.fixture()
def cfg(tmp_path: Path) -> ConfigManager:
    c = ConfigManager(config_file=tmp_path / "config.toml")
    c.load()
    return c


@pytest.fixture()
def api(registry, cfg) -> PluginAPI:
    return PluginAPI(
        plugin_name="test_plugin",
        registry=registry,
        config_manager=cfg,
    )


class TestPluginAPIRegisterCommand:
    def test_register_command_returns_true(self, api):
        result = api.register_command("hello", MagicMock())
        assert result is True

    def test_register_duplicate_returns_false(self, api):
        api.register_command("hello", MagicMock())
        result = api.register_command("hello", MagicMock())
        assert result is False

    def test_register_command_stored_in_registry(self, api, registry):
        api.register_command("hello", MagicMock())
        assert registry.has("hello")

    def test_register_command_stores_plugin_name(self, api, registry):
        api.register_command("hello", MagicMock())
        cmd = registry.get("hello")
        assert cmd.plugin_name == "test_plugin"


class TestPluginAPIRegisterHelp:
    def test_register_help_stores_entry(self, api):
        api.register_help(
            command="hello",
            description="Say hello",
            usage="hello",
            examples="hello",
        )
        entries = api.get_help_entries()
        assert "hello" in entries
        assert entries["hello"]["description"] == "Say hello"

    def test_get_help_entries_returns_copy(self, api):
        api.register_help("hello", "desc", "usage", "examples")
        entries = api.get_help_entries()
        entries["hello"] = None
        assert api.get_help_entries()["hello"] is not None


class TestPluginAPIGetConfig:
    def test_returns_empty_dict_when_no_plugin_config(self, api):
        result = api.get_config()
        assert result == {}

    def test_returns_plugin_specific_config(self, api, cfg):
        cfg.set_plugin_config("test_plugin", "key", "value")
        result = api.get_config()
        assert result.get("key") == "value"


class TestPluginAPIOutput:
    def test_print_output(self, api, capsys):
        api.print_output("hello")
        assert "hello" in capsys.readouterr().out

    def test_print_success(self, api, capsys):
        api.print_success("ok")
        assert "ok" in capsys.readouterr().out

    def test_print_error(self, api, capsys):
        api.print_error("bad")
        assert "bad" in capsys.readouterr().out

    def test_print_info(self, api, capsys):
        api.print_info("note")
        assert "note" in capsys.readouterr().out

    def test_print_warning(self, api, capsys):
        api.print_warning("careful")
        assert "careful" in capsys.readouterr().out


class TestPluginAPIProperties:
    def test_plugin_name_property(self, api):
        assert api.plugin_name == "test_plugin"
