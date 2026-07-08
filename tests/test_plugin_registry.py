"""
test_plugin_registry.py
Unit tests for rshx.core.plugin_registry.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from rshx.core.plugin_registry import PluginRegistry, PluginCommand
from rshx.core.repl import ShellState
from rshx.core.config import ConfigManager


@pytest.fixture()
def registry() -> PluginRegistry:
    return PluginRegistry()


@pytest.fixture()
def state(tmp_path: Path) -> ShellState:
    os.chdir(tmp_path)
    cfg = ConfigManager(config_file=tmp_path / "config.toml")
    cfg.load()
    s = ShellState(cwd=tmp_path)
    s.config_manager = cfg
    return s


class TestPluginRegistryRegister:
    def test_register_new_command(self, registry):
        handler = MagicMock()
        result = registry.register("hello", handler, "test_plugin")
        assert result is True
        assert registry.has("hello")

    def test_register_duplicate_returns_false(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "plugin_a")
        result = registry.register("hello", handler, "plugin_b")
        assert result is False

    def test_register_stores_plugin_name(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "my_plugin")
        cmd = registry.get("hello")
        assert cmd.plugin_name == "my_plugin"

    def test_register_stores_description(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "my_plugin", description="Say hello")
        cmd = registry.get("hello")
        assert cmd.description == "Say hello"


class TestPluginRegistryUnregister:
    def test_unregister_plugin_removes_commands(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "my_plugin")
        registry.register("greet", handler, "my_plugin")
        removed = registry.unregister_plugin("my_plugin")
        assert "hello" in removed
        assert "greet" in removed
        assert not registry.has("hello")
        assert not registry.has("greet")

    def test_unregister_nonexistent_plugin_returns_empty(self, registry):
        removed = registry.unregister_plugin("nonexistent")
        assert removed == []

    def test_unregister_only_removes_own_commands(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "plugin_a")
        registry.register("bye", handler, "plugin_b")
        registry.unregister_plugin("plugin_a")
        assert not registry.has("hello")
        assert registry.has("bye")


class TestPluginRegistryLookup:
    def test_get_returns_command(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "my_plugin")
        cmd = registry.get("hello")
        assert isinstance(cmd, PluginCommand)
        assert cmd.name == "hello"

    def test_get_returns_none_for_missing(self, registry):
        assert registry.get("missing") is None

    def test_has_returns_true(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "my_plugin")
        assert registry.has("hello") is True

    def test_has_returns_false(self, registry):
        assert registry.has("missing") is False

    def test_all_returns_copy(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "my_plugin")
        result = registry.all()
        result["hello"] = None
        assert registry.get("hello") is not None

    def test_count(self, registry):
        handler = MagicMock()
        registry.register("a", handler, "p")
        registry.register("b", handler, "p")
        assert registry.count() == 2

    def test_commands_for_plugin(self, registry):
        handler = MagicMock()
        registry.register("hello", handler, "plugin_a")
        registry.register("bye", handler, "plugin_b")
        result = registry.commands_for_plugin("plugin_a")
        assert result == ["hello"]


class TestPluginRegistryDispatch:
    def test_dispatch_calls_handler(self, registry, state):
        handler = MagicMock()
        registry.register("hello", handler, "my_plugin")
        result = registry.dispatch("hello", ["arg1"], state)
        assert result is True
        handler.assert_called_once_with(["arg1"], state)

    def test_dispatch_returns_false_for_missing(self, registry, state):
        result = registry.dispatch("missing", [], state)
        assert result is False

    def test_dispatch_handles_handler_exception(self, registry, state, capsys):
        def broken(args, s):
            raise RuntimeError("oops")
        registry.register("broken", broken, "my_plugin")
        result = registry.dispatch("broken", [], state)
        assert result is True
        assert "Error" in capsys.readouterr().out
