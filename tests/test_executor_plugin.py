"""
test_executor_plugin.py
Covers executor.py lines 67-68 - plugin registry dispatch path.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from rshx.core.executor import execute
from rshx.core.ast import CommandNode, RedirectNode, PipelineNode
from rshx.core.repl import ShellState
from rshx.core.config import ConfigManager
from rshx.core.plugin_registry import PluginRegistry
from rshx.core.plugin_manager import PluginManager


@pytest.fixture()
def state_with_registry(tmp_path: Path) -> ShellState:
    os.chdir(tmp_path)
    cfg = ConfigManager(config_file=tmp_path / "config.toml")
    cfg.load()
    registry = PluginRegistry()
    pm = PluginManager(
        registry=registry,
        config_manager=cfg,
        plugins_dir=tmp_path / "plugins",
    )
    s = ShellState(cwd=tmp_path)
    s.config_manager = cfg
    s.plugin_manager = pm
    return s


def single_pipeline(name, args=None):
    return PipelineNode(stages=[
        RedirectNode(command=CommandNode(name=name, args=args or []))
    ])


class TestExecutorPluginRouting:
    def test_plugin_command_is_dispatched(self, state_with_registry):
        """Covers executor.py lines 67-68."""
        handler = MagicMock()
        state_with_registry.plugin_manager._registry.register(
            "myplugin_cmd", handler, "test_plugin"
        )
        pipeline = single_pipeline("myplugin_cmd")
        execute(pipeline, state_with_registry)
        handler.assert_called_once()

    def test_plugin_command_not_called_when_not_registered(self, state_with_registry):
        pipeline = single_pipeline("nonexistent_plugin_cmd")
        execute(pipeline, state_with_registry)
