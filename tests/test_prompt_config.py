"""
test_prompt_config.py
Unit tests for rshx.core.prompt_config.
"""

from pathlib import Path
from unittest.mock import patch
from prompt_toolkit.formatted_text import HTML

from rshx.core.prompt_config import build_prompt, _get_git_branch
from rshx.core.theme import get_theme


class TestBuildPrompt:
    def setup_method(self):
        self.theme = get_theme("default")
        self.cwd = Path("C:/Projects/rshx")

    def test_returns_html_instance(self):
        result = build_prompt(self.cwd, self.theme)
        assert isinstance(result, HTML)

    def test_contains_rshx_label(self):
        result = build_prompt(self.cwd, self.theme)
        assert "RSHX" in result.value

    def test_contains_cwd_when_show_cwd_true(self):
        result = build_prompt(self.cwd, self.theme, show_cwd=True)
        assert str(self.cwd) in result.value

    def test_no_cwd_when_show_cwd_false(self):
        result = build_prompt(self.cwd, self.theme, show_cwd=False)
        assert str(self.cwd) not in result.value

    def test_contains_gt_symbol(self):
        result = build_prompt(self.cwd, self.theme, show_cwd=True)
        assert "&gt;" in result.value

    def test_contains_newline(self):
        result = build_prompt(self.cwd, self.theme)
        assert "\n" in result.value

    def test_custom_shell_name(self):
        result = build_prompt(self.cwd, self.theme, shell_name="MYSHELL")
        assert "MYSHELL" in result.value

    def test_git_branch_shown_when_enabled(self, tmp_path: Path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n")
        result = build_prompt(tmp_path, self.theme, show_git_branch=True)
        assert "main" in result.value

    def test_git_branch_not_shown_when_disabled(self, tmp_path: Path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n")
        result = build_prompt(tmp_path, self.theme, show_git_branch=False)
        assert "[main]" not in result.value

    def test_different_themes_produce_different_colours(self):
        dark = get_theme("dark")
        light = get_theme("light")
        result_dark = build_prompt(self.cwd, dark)
        result_light = build_prompt(self.cwd, light)
        assert result_dark.value != result_light.value


class TestGetGitBranch:
    def test_returns_branch_name(self, tmp_path: Path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/feature-x\n")
        result = _get_git_branch(tmp_path)
        assert result == "feature-x"

    def test_returns_none_outside_repo(self, tmp_path: Path):
        result = _get_git_branch(tmp_path)
        assert result is None

    def test_handles_detached_head(self, tmp_path: Path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("abc1234def5678\n")
        result = _get_git_branch(tmp_path)
        assert result == "abc1234"

    def test_handles_os_error_gracefully(self, tmp_path: Path):
        with patch("rshx.core.prompt_config.Path.exists", side_effect=OSError):
            result = _get_git_branch(tmp_path)
        assert result is None
