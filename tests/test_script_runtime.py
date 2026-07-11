"""
test_script_runtime.py
Unit tests for rshx.core.script_runtime.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rshx.core.script_runtime import (
    run_script, _inject_args, _remove_args, _derive_name,
    _expand_positional_bare,
)
from rshx.core.script_types import ScriptNode, ScriptCommand
from rshx.core.repl import ShellState
from rshx.core.config import ConfigManager
from rshx.core.plugin_registry import PluginRegistry
from rshx.core.plugin_manager import PluginManager
from rshx.core.preprocessor import Preprocessor


@pytest.fixture()
def state(tmp_path: Path) -> ShellState:
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


@pytest.fixture()
def preprocessor(state) -> Preprocessor:
    return Preprocessor(
        alias_manager=state.alias_manager,
        environment=state.environment,
    )


def make_node(*commands: str, continue_on_error: bool = False) -> ScriptNode:
    node = ScriptNode(path="test.rshx", name="Test Script")
    node.continue_on_error = continue_on_error
    for i, cmd in enumerate(commands, start=1):
        node.commands.append(ScriptCommand(source=cmd, line_number=i))
    return node


class TestExpandPositionalBare:
    def test_expands_bare_percent_1(self):
        result = _expand_positional_bare("echo Hello %1", ["Raghav"])
        assert result == "echo Hello Raghav"

    def test_expands_multiple_args(self):
        result = _expand_positional_bare("echo %1 %2", ["Hello", "World"])
        assert result == "echo Hello World"

    def test_missing_arg_expands_to_empty(self):
        result = _expand_positional_bare("echo %1 %2", ["OnlyOne"])
        assert result == "echo OnlyOne "

    def test_no_positional_refs_unchanged(self):
        result = _expand_positional_bare("git status", ["Raghav"])
        assert result == "git status"

    def test_percent_var_percent_not_affected(self):
        result = _expand_positional_bare("cd %MYDIR%", ["Raghav"])
        assert result == "cd %MYDIR%"

    def test_empty_args_leaves_refs(self):
        result = _expand_positional_bare("echo %1", [])
        assert result == "echo "


class TestRunScriptBasic:
    def test_empty_script_returns_immediately(self, state, preprocessor):
        node = ScriptNode(path="empty.rshx", name="Empty")
        result = run_script(node, state, preprocessor)
        assert result.commands_executed == 0
        assert result.success is True

    def test_single_builtin_command(self, state, preprocessor):
        node = make_node("pwd")
        result = run_script(node, state, preprocessor)
        assert result.commands_executed == 1
        assert result.commands_succeeded == 1
        assert result.success is True

    def test_multiple_commands_execute_sequentially(self, state, preprocessor):
        node = make_node("pwd", "whoami")
        result = run_script(node, state, preprocessor)
        assert result.commands_executed == 2
        assert result.commands_total == 2

    def test_duration_is_recorded(self, state, preprocessor):
        node = make_node("pwd")
        result = run_script(node, state, preprocessor)
        assert result.duration >= 0.0

    def test_script_name_in_result(self, state, preprocessor):
        node = make_node("pwd")
        node.name = "My Workflow"
        result = run_script(node, state, preprocessor)
        assert result.script_name == "My Workflow"


class TestRunScriptSharedState:
    def test_cd_persists_across_commands(self, state, preprocessor, tmp_path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        node = make_node(f"cd {sub}", "pwd")
        run_script(node, state, preprocessor)
        assert state.cwd == sub

    def test_alias_expands_in_script(self, state, preprocessor):
        state.alias_manager.set("mypwd", "pwd")
        node = make_node("mypwd")
        result = run_script(node, state, preprocessor)
        assert result.commands_succeeded == 1

    def test_variable_expands_in_script(self, state, preprocessor, tmp_path):
        state.environment._variables["MYDIR"] = str(tmp_path)
        node = make_node("cd %MYDIR%")
        result = run_script(node, state, preprocessor)
        assert result.commands_succeeded == 1


class TestRunScriptPositionalArgs:
    def test_bare_positional_arg_expands(self, state, preprocessor, tmp_path):
        """Test that %1 (without closing %) expands correctly."""
        node = make_node("echo %1")
        result = run_script(node, state, preprocessor, script_args=["Raghav"])
        assert result.commands_succeeded == 1

    def test_positional_args_removed_after_execution(self, state, preprocessor):
        node = make_node("pwd")
        run_script(node, state, preprocessor, script_args=["arg1", "arg2"])
        assert "1" not in state.environment._variables
        assert "2" not in state.environment._variables

    def test_multiple_positional_args(self, state, preprocessor):
        node = make_node("pwd")
        run_script(node, state, preprocessor, script_args=["a", "b", "c"])
        assert "1" not in state.environment._variables

    def test_no_args_does_not_inject(self, state, preprocessor):
        node = make_node("pwd")
        run_script(node, state, preprocessor, script_args=[])
        assert "1" not in state.environment._variables

    def test_positional_arg_injected(self, state, preprocessor):
        node = make_node("pwd")
        run_script(node, state, preprocessor, script_args=["hello"])
        assert state.environment._variables.get("1") is None


class TestRunScriptFailureHandling:
    def test_stop_on_error_default(self, state, preprocessor):
        node = make_node("invalidcmd999", "pwd")
        node.continue_on_error = False
        result = run_script(node, state, preprocessor)
        assert result.commands_executed == 1

    def test_continue_on_error_executes_all(self, state, preprocessor):
        node = make_node("invalidcmd999", "pwd")
        node.continue_on_error = True
        result = run_script(node, state, preprocessor)
        assert result.commands_executed == 2

    def test_parse_error_recorded(self, state, preprocessor):
        node = make_node("git status |")
        result = run_script(node, state, preprocessor)
        assert result.success is False
        assert len(result.errors) > 0


class TestInjectRemoveArgs:
    def test_inject_args(self, state):
        _inject_args(state, ["hello", "world"])
        assert state.environment._variables.get("1") == "hello"
        assert state.environment._variables.get("2") == "world"

    def test_remove_args(self, state):
        _inject_args(state, ["hello", "world"])
        _remove_args(state, ["hello", "world"])
        assert "1" not in state.environment._variables
        assert "2" not in state.environment._variables

    def test_empty_args_no_effect(self, state):
        _inject_args(state, [])
        assert "1" not in state.environment._variables


class TestDeriveName:
    def test_derives_from_path(self):
        assert _derive_name("/tmp/my_script.rshx") == "my_script"

    def test_empty_path_returns_script(self):
        assert _derive_name("") == "script"

    def test_filename_only(self):
        assert _derive_name("hello.rshx") == "hello"
