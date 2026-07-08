"""
test_plugin_builtins.py
Tests for plugin-related builtin coverage gaps in cmd_plugin.
Covers builtins.py lines 422-430, 440-449, 456, 466, 476.
"""

import os
from pathlib import Path
import pytest

from rshx.commands.builtins import cmd_plugin
from rshx.core.repl import ShellState
from rshx.core.config import ConfigManager
from rshx.core.plugin_registry import PluginRegistry
from rshx.core.plugin_manager import PluginManager


VALID_MANIFEST = '''
name = "demo"
version = "1.0.0"
description = "Demo plugin"
author = "Tester"
commands = ["demo_cmd"]
'''

VALID_CODE = '''
def initialise(api):
    api.register_command("demo_cmd", _handler, "Demo command")

def shutdown():
    pass

def _handler(args, shell_state):
    pass
'''


def make_plugin(plugins_dir, name, manifest, code):
    d = plugins_dir / name
    d.mkdir(parents=True)
    (d / "manifest.toml").write_text(manifest, encoding="utf-8")
    (d / "plugin.py").write_text(code, encoding="utf-8")
    return d


@pytest.fixture()
def state_with_plugin(tmp_path):
    os.chdir(tmp_path)
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    make_plugin(plugins_dir, "demo", VALID_MANIFEST, VALID_CODE)

    cfg = ConfigManager(config_file=tmp_path / "config.toml")
    cfg.load()
    registry = PluginRegistry()
    pm = PluginManager(registry=registry, config_manager=cfg, plugins_dir=plugins_dir)
    pm.discover_and_load_all()

    s = ShellState(cwd=tmp_path)
    s.config_manager = cfg
    s.plugin_manager = pm
    return s


class TestCmdPluginWithLoadedPlugin:
    def test_plugin_list_shows_loaded_plugin(self, state_with_plugin, capsys):
        """Covers builtins.py lines 422-430."""
        cmd_plugin(["list"], state_with_plugin)
        captured = capsys.readouterr()
        assert "demo" in captured.out
        assert "enabled" in captured.out

    def test_plugin_info_shows_detail(self, state_with_plugin, capsys):
        """Covers builtins.py lines 440-449."""
        cmd_plugin(["info", "demo"], state_with_plugin)
        captured = capsys.readouterr()
        assert "demo" in captured.out
        assert "1.0.0" in captured.out
        assert "Demo plugin" in captured.out

    def test_plugin_disable_success(self, state_with_plugin, capsys):
        """Covers builtins.py line 466."""
        cmd_plugin(["disable", "demo"], state_with_plugin)
        captured = capsys.readouterr()
        assert "disabled" in captured.out.lower()

    def test_plugin_enable_after_disable(self, state_with_plugin, capsys):
        """Covers builtins.py line 456."""
        state_with_plugin.plugin_manager.disable("demo")
        capsys.readouterr()
        cmd_plugin(["enable", "demo"], state_with_plugin)
        captured = capsys.readouterr()
        assert "enabled" in captured.out.lower()

    def test_plugin_reload_success(self, state_with_plugin, capsys):
        """Covers builtins.py line 476."""
        cmd_plugin(["reload", "demo"], state_with_plugin)
        captured = capsys.readouterr()
        assert "reloaded" in captured.out.lower()
