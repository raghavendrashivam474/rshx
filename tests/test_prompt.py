"""
test_prompt.py
Unit tests for rshx.core.prompt.
"""

from pathlib import Path
from prompt_toolkit.formatted_text import HTML

from rshx.core.prompt import build_prompt


class TestBuildPrompt:
    def test_returns_html_instance(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert isinstance(result, HTML)

    def test_prompt_contains_cwd(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert str(tmp_path) in result.value

    def test_prompt_contains_rshx_label(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert "RSHX" in result.value

    def test_prompt_contains_gt_symbol(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert "&gt;" in result.value

    def test_prompt_contains_newline(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert "\n" in result.value

    def test_prompt_reflects_different_paths(self):
        path_a = Path("C:/Users/test")
        path_b = Path("C:/Projects/rshx")
        result_a = build_prompt(path_a)
        result_b = build_prompt(path_b)
        assert str(path_a) in result_a.value
        assert str(path_b) in result_b.value
        assert str(path_a) not in result_b.value
