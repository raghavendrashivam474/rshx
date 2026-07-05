"""
test_display.py
Unit tests for rshx.utils.display.
"""

from unittest.mock import patch
from rshx.utils.display import (
    initialise_display,
    print_banner,
    print_output,
    print_success,
    print_warning,
    print_error,
    print_info,
    suggest_command,
)


class TestInitialiseDisplay:
    def test_calls_colorama_init(self):
        with patch("rshx.utils.display.colorama_init") as mock_init:
            initialise_display()
        mock_init.assert_called_once_with(autoreset=True)


class TestPrintBanner:
    def test_banner_produces_output(self, capsys):
        print_banner()
        captured = capsys.readouterr()
        assert "RSHX" in captured.out or "Raghav" in captured.out


class TestPrintHelpers:
    def test_print_output(self, capsys):
        print_output("hello")
        assert "hello" in capsys.readouterr().out

    def test_print_success(self, capsys):
        print_success("ok")
        assert "ok" in capsys.readouterr().out

    def test_print_warning(self, capsys):
        print_warning("careful")
        assert "careful" in capsys.readouterr().out

    def test_print_error(self, capsys):
        print_error("bad")
        assert "bad" in capsys.readouterr().out

    def test_print_info(self, capsys):
        print_info("note")
        assert "note" in capsys.readouterr().out


class TestSuggestCommand:
    def test_suggests_close_match(self, capsys):
        suggest_command("pythn", ["python", "git", "help"])
        captured = capsys.readouterr()
        assert "python" in captured.out

    def test_no_suggestion_for_distant_input(self, capsys):
        suggest_command("zzzzz", ["python", "git", "help"])
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_suggests_multiple_matches(self, capsys):
        suggest_command("hel", ["help", "hello", "git"])
        captured = capsys.readouterr()
        assert "help" in captured.out

    def test_empty_candidates_prints_error(self, capsys):
        suggest_command("anything", [])
        captured = capsys.readouterr()
        assert "Error" in captured.out
