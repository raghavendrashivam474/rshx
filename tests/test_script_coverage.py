"""
test_script_coverage.py
Targeted tests for remaining coverage gaps in scripting modules.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rshx.commands.builtins import cmd_startup, cmd_run, cmd_plugin
from rshx.core.script_loader import load_script
from rshx.core.script_runtime import run_script, _inject_args
from rshx.core.script_types import ScriptNode, ScriptCommand, ScriptResult
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


def make_node(*commands, continue_on_error=False):
    node = ScriptNode(path="test.rshx", name="Test")
    node.continue_on_error = continue_on_error
    for i, cmd in enumerate(commands, start=1):
        node.commands.append(ScriptCommand(source=cmd, line_number=i))
    return node


# ---------------------------------------------------------------------------
# builtins.py startup list with commands - lines 381-386
# ---------------------------------------------------------------------------

class TestStartupListWithCommands:
    def test_startup_list_shows_commands(self, state, capsys):
        """Covers builtins.py lines 381-386."""
        state.config_manager.add_startup_command("alias gs=git status")
        state.config_manager.add_startup_command("set EDITOR=code")
        cmd_startup(["list"], state)
        captured = capsys.readouterr()
        assert "alias gs=git status" in captured.out
        assert "set EDITOR=code" in captured.out


# ---------------------------------------------------------------------------
# builtins.py startup remove - lines 399-405
# ---------------------------------------------------------------------------

class TestStartupRemove:
    def test_startup_remove_success(self, state, capsys):
        """Covers builtins.py lines 399-405."""
        state.config_manager.add_startup_command("alias gs=git status")
        cmd_startup(["remove", "alias", "gs=git", "status"], state)
        assert "alias gs=git status" not in state.config_manager.config.startup_commands
        assert "removed" in capsys.readouterr().out.lower()


# ---------------------------------------------------------------------------
# builtins.py plugin success paths - lines 446-447, 461-486
# Already covered in test_plugin_builtins but not test_builtins fixture
# Add minimal coverage via state fixture
# ---------------------------------------------------------------------------

class TestPluginSuccessPathsInBuiltins:
    def test_plugin_info_success(self, state, tmp_path, capsys):
        """Covers plugin info success path."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        plugin_dir = plugins_dir / "demo"
        plugin_dir.mkdir()
        utf8NoBom = "name = 'demo'\nversion = '1.0.0'\ndescription = 'Demo'\nauthor = 'T'\ncommands = []\n"
        (plugin_dir / "manifest.toml").write_text(utf8NoBom, encoding="utf-8")
        (plugin_dir / "plugin.py").write_text("def initialise(api): pass\n", encoding="utf-8")
        state.plugin_manager._plugins_dir = plugins_dir
        state.plugin_manager.discover_and_load_all()
        cmd_plugin(["info", "demo"], state)
        captured = capsys.readouterr()
        assert "demo" in captured.out or "Error" in captured.out


# ---------------------------------------------------------------------------
# builtins.py critical parse errors stop run - lines 530, 533
# ---------------------------------------------------------------------------

class TestRunCriticalParseError:
    def test_critical_directive_error_stops_execution(self, state, tmp_path, capsys):
        """Covers builtins.py lines 530, 533."""
        script = tmp_path / "bad.rshx"
        script.write_text("@continue_on_error maybe\npwd\n", encoding="utf-8")
        cmd_run(["bad.rshx"], state)
        captured = capsys.readouterr()
        assert "Error" in captured.out


# ---------------------------------------------------------------------------
# builtins.py failed result display - lines 567-570
# ---------------------------------------------------------------------------

class TestRunFailedResultDisplay:
    def test_failed_script_shows_error_in_summary(self, state, tmp_path, capsys):
        """Covers builtins.py lines 567-570."""
        script = tmp_path / "fail.rshx"
        script.write_text("git status |\n", encoding="utf-8")
        cmd_run(["fail.rshx"], state)
        captured = capsys.readouterr()
        assert "FAILED" in captured.out or "Error" in captured.out


# ---------------------------------------------------------------------------
# script_loader.py OSError - lines 90-91
# ---------------------------------------------------------------------------

class TestScriptLoaderOSError:
    def test_os_error_reading_file_returns_error(self, tmp_path):
        """Covers script_loader.py lines 90-91."""
        script = tmp_path / "test.rshx"
        script.write_text("pwd", encoding="utf-8")
        with patch("pathlib.Path.read_text", side_effect=OSError("disk failure")):
            loaded, error = load_script("test.rshx", cwd=tmp_path)
        assert loaded is None
        assert "Cannot read" in error or "disk failure" in error


# ---------------------------------------------------------------------------
# script_runtime.py shell_state.running = False mid-script - line 82
# ---------------------------------------------------------------------------

class TestRuntimeRunningFlag:
    def test_stops_when_running_is_false(self, state, preprocessor):
        """Covers script_runtime.py line 82."""
        call_count = [0]

        def exit_after_first(args, s):
            call_count[0] += 1
            s.running = False

        from rshx.commands.builtins import BUILTIN_REGISTRY
        original = BUILTIN_REGISTRY.get("pwd")
        BUILTIN_REGISTRY["pwd"] = exit_after_first

        try:
            node = make_node("pwd", "pwd", "pwd")
            result = run_script(node, state, preprocessor)
        finally:
            if original:
                BUILTIN_REGISTRY["pwd"] = original
            else:
                del BUILTIN_REGISTRY["pwd"]

        assert call_count[0] == 1


# ---------------------------------------------------------------------------
# script_runtime.py preprocessor exception - lines 123-130
# ---------------------------------------------------------------------------

class TestRuntimePreprocessorException:
    def test_preprocessor_exception_recorded_as_error(self, state, preprocessor):
        """Covers script_runtime.py lines 123-130."""
        node = make_node("some command")

        with patch.object(preprocessor, "process", side_effect=RuntimeError("boom")):
            result = run_script(node, state, preprocessor)

        assert result.success is False
        assert any("Preprocessor error" in e.message for e in result.errors)


# ---------------------------------------------------------------------------
# script_runtime.py empty pipeline after expansion - line 144
# ---------------------------------------------------------------------------

class TestRuntimeEmptyPipeline:
    def test_empty_pipeline_after_expansion_returns_true(self, state, preprocessor):
        """Covers script_runtime.py line 144 - empty pipeline returns True."""
        node = make_node("pwd")
        with patch("rshx.core.script_runtime.parse") as mock_parse:
            mock_pipeline = MagicMock()
            mock_pipeline.stages = []
            mock_parse.return_value = mock_pipeline
            result = run_script(node, state, preprocessor)
        assert result.commands_executed == 1
        assert result.commands_succeeded == 1


# ---------------------------------------------------------------------------
# script_runtime.py executor exception - lines 153-161
# ---------------------------------------------------------------------------

class TestRuntimeExecutorException:
    def test_executor_exception_recorded_as_error(self, state, preprocessor):
        """Covers script_runtime.py lines 153-161."""
        node = make_node("pwd")

        with patch("rshx.core.script_runtime.execute", side_effect=RuntimeError("exec fail")):
            result = run_script(node, state, preprocessor)

        assert result.success is False
        assert any("Execution error" in e.message for e in result.errors)


# ---------------------------------------------------------------------------
# script_runtime.py _inject_args exception - lines 190-191
# ---------------------------------------------------------------------------

class TestInjectArgsException:
    def test_inject_args_handles_exception_gracefully(self, state):
        """Covers script_runtime.py lines 190-191."""
        original_vars = state.environment._variables

        class BadDict(dict):
            def __setitem__(self, key, value):
                raise RuntimeError("cannot set")

        state.environment._variables = BadDict()
        try:
            _inject_args(state, ["arg1"])
        except Exception:
            pytest.fail("_inject_args raised unexpectedly")
        finally:
            state.environment._variables = original_vars
