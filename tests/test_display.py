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
)


class TestInitialiseDisplay:
    def test_calls_colorama_init(self):
        """initialise_display should call colorama_init with autoreset=True."""
        with patch("rshx.utils.display.colorama_init") as mock_init:
            initialise_display()
        mock_init.assert_called_once_with(autoreset=True)


class TestPrintBanner:
    def test_banner_produces_output(self, capsys):
        """print_banner should write something to stdout."""
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
