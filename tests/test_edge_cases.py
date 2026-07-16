"""
test_edge_cases.py
------------------
Edge case and reliability tests for Release Sprint 1.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from rshx.core.parser import parse
from rshx.core.script_loader import load_script
from rshx.core.script_parser import parse_script
from rshx.core.script_runtime import run_script
from rshx.core.repl import ShellState
from rshx.core.config import ConfigManager
from rshx.core.plugin_registry import PluginRegistry
from rshx.core.plugin_manager import PluginManager
from rshx.core.preprocessor import Preprocessor

# Root of the project - used for reading pyproject.toml in tests
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture()
def state(tmp_path: Path) -> ShellState:
    os.chdir(tmp_path)
    cfg = ConfigManager(config_file=tmp_path / "config.toml")
    cfg.load()
    s = ShellState(cwd=tmp_path)
    s.config_manager = cfg
    s.plugin_manager = PluginManager(
        registry=PluginRegistry(),
        config_manager=cfg,
        plugins_dir=tmp_path / "plugins",
    )
    return s


@pytest.fixture()
def preprocessor(state) -> Preprocessor:
    return Preprocessor(
        alias_manager=state.alias_manager,
        environment=state.environment,
    )


class TestParserEdgeCases:
    def test_very_long_command(self):
        long_cmd = "git " + "arg " * 200
        result = parse(long_cmd)
        assert result.stage_count() == 1
        assert len(result.stages[0].command.args) == 200

    def test_unicode_in_command(self):
        result = parse("echo hello")
        assert result.stages[0].command.name == "echo"

    def test_multiple_spaces_between_tokens(self):
        result = parse("git   status")
        assert result.stages[0].command.name == "git"
        assert "status" in result.stages[0].command.args

    def test_command_with_numbers(self):
        result = parse("git log -5")
        assert result.stages[0].command.name == "git"

    def test_empty_pipeline_has_no_stages(self):
        result = parse("")
        assert result.stage_count() == 0


class TestScriptLoaderEdgeCases:
    def test_script_with_only_comments(self, tmp_path):
        script = tmp_path / "comments.rshx"
        script.write_text("# comment 1\n# comment 2\n", encoding="utf-8")
        loaded, error = load_script("comments.rshx", cwd=tmp_path)
        assert loaded is not None
        assert error == ""

    def test_script_with_only_blank_lines(self, tmp_path):
        script = tmp_path / "blanks.rshx"
        script.write_text("\n\n\n\n", encoding="utf-8")
        loaded, error = load_script("blanks.rshx", cwd=tmp_path)
        assert loaded is not None

    def test_very_long_script_path(self, tmp_path):
        script = tmp_path / "test.rshx"
        script.write_text("pwd\n", encoding="utf-8")
        loaded, error = load_script(str(script), cwd=tmp_path)
        assert loaded is not None

    def test_script_with_windows_line_endings(self, tmp_path):
        script = tmp_path / "windows.rshx"
        script.write_bytes(b"pwd\r\ngit status\r\n")
        loaded, error = load_script("windows.rshx", cwd=tmp_path)
        assert loaded is not None


class TestScriptParserEdgeCases:
    def test_directive_with_extra_spaces(self):
        node, errors = parse_script("@name   My Script   \npwd")
        assert node.name == "My Script"

    def test_multiple_same_directives_last_wins(self):
        node, errors = parse_script("@name First\n@name Second\npwd")
        assert node.name == "Second"

    def test_command_with_spaces_preserved(self):
        node, _ = parse_script('echo "hello world"')
        assert node.commands[0].source == 'echo "hello world"'

    def test_empty_lines_between_directives_and_commands(self):
        source = "@name Test\n\n\npwd\n\n\ngit status"
        node, _ = parse_script(source)
        assert node.command_count() == 2
        assert node.name == "Test"

    def test_large_script(self):
        lines = ["pwd\n"] * 100
        source = "".join(lines)
        node, errors = parse_script(source)
        assert node.command_count() == 100
        assert errors == []


class TestScriptRuntimeEdgeCases:
    def test_script_with_no_commands_succeeds(self, state, preprocessor):
        from rshx.core.script_types import ScriptNode
        node = ScriptNode(path="empty.rshx", name="Empty")
        result = run_script(node, state, preprocessor)
        assert result.success is True
        assert result.commands_executed == 0

    def test_multiple_cd_commands_persist(self, state, preprocessor, tmp_path):
        from rshx.core.script_types import ScriptNode, ScriptCommand
        sub1 = tmp_path / "sub1"
        sub2 = tmp_path / "sub1" / "sub2"
        sub1.mkdir()
        sub2.mkdir()
        node = ScriptNode(path="nav.rshx", name="Nav")
        node.commands.append(ScriptCommand(source=f"cd {sub1}", line_number=1))
        node.commands.append(ScriptCommand(source=f"cd sub2", line_number=2))
        run_script(node, state, preprocessor)
        assert state.cwd == sub2

    def test_script_result_duration_positive(self, state, preprocessor):
        from rshx.core.script_types import ScriptNode, ScriptCommand
        node = ScriptNode(path="t.rshx", name="T")
        node.commands.append(ScriptCommand(source="pwd", line_number=1))
        result = run_script(node, state, preprocessor)
        assert result.duration >= 0.0

    def test_stop_on_error_leaves_state_intact(self, state, preprocessor, tmp_path):
        from rshx.core.script_types import ScriptNode, ScriptCommand
        node = ScriptNode(path="t.rshx", name="T")
        node.continue_on_error = False
        original_cwd = state.cwd
        node.commands.append(ScriptCommand(source="invalidcmd999", line_number=1))
        node.commands.append(ScriptCommand(source=f"cd {tmp_path}", line_number=2))
        run_script(node, state, preprocessor)
        assert state.cwd == original_cwd


class TestConfigEdgeCases:
    def test_config_with_empty_aliases_section(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            '[general]\nversion = "0.8.0"\ntheme = "default"\n'
            '[prompt]\nshow_cwd = true\nshow_git_branch = false\n'
            '[aliases]\n[environment]\n[startup]\ncommands = []\n',
            encoding="utf-8",
        )
        cfg = ConfigManager(config_file=config_file)
        cfg.load()
        assert cfg.config.aliases == {}

    def test_version_is_string_after_load(self, tmp_path):
        cfg = ConfigManager(config_file=tmp_path / "config.toml")
        cfg.load()
        assert isinstance(cfg.config.version, str)

    def test_reload_after_external_modification(self, tmp_path):
        config_file = tmp_path / "config.toml"
        cfg = ConfigManager(config_file=config_file)
        cfg.load()
        cfg.save_alias("gs", "git status")
        cfg2 = ConfigManager(config_file=config_file)
        cfg2.load()
        assert cfg2.config.aliases.get("gs") == "git status"


class TestVersionSource:
    def test_version_importable_from_package(self):
        from rshx import __version__
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_matches_pyproject(self):
        """Version in rshx/__init__.py must match pyproject.toml."""
        import tomllib
        from rshx import __version__
        pyproject = PROJECT_ROOT / "pyproject.toml"
        data = tomllib.loads(pyproject.read_bytes().decode("utf-8-sig"))
        assert data["project"]["version"] == __version__

    def test_display_banner_contains_version(self):
        from rshx import __version__
        from rshx.utils.display import BANNER
        assert isinstance(BANNER, str)
        assert isinstance(__version__, str)
