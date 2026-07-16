"""
test_confirmation.py
Unit tests for rshx.core.confirmation.
"""

from unittest.mock import patch
import pytest

from rshx.core.confirmation import confirm, confirm_destructive


class TestConfirm:
    def test_yes_input_returns_true(self):
        with patch("builtins.input", return_value="y"):
            assert confirm("Delete?") is True

    def test_yes_full_word_returns_true(self):
        with patch("builtins.input", return_value="yes"):
            assert confirm("Delete?") is True

    def test_no_input_returns_false(self):
        with patch("builtins.input", return_value="n"):
            assert confirm("Delete?") is False

    def test_empty_input_defaults_to_false(self):
        with patch("builtins.input", return_value=""):
            assert confirm("Delete?") is False

    def test_empty_input_with_default_true_returns_true(self):
        with patch("builtins.input", return_value=""):
            assert confirm("Delete?", default=True) is True

    def test_uppercase_y_returns_true(self):
        with patch("builtins.input", return_value="Y"):
            assert confirm("Delete?") is True

    def test_uppercase_yes_returns_true(self):
        with patch("builtins.input", return_value="YES"):
            assert confirm("Delete?") is True

    def test_random_input_returns_false(self):
        with patch("builtins.input", return_value="maybe"):
            assert confirm("Delete?") is False

    def test_eof_error_returns_false(self):
        with patch("builtins.input", side_effect=EOFError):
            assert confirm("Delete?") is False

    def test_keyboard_interrupt_returns_false(self):
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            assert confirm("Delete?") is False


class TestConfirmDestructive:
    def test_confirmed_returns_true(self, capsys):
        with patch("builtins.input", return_value="y"):
            result = confirm_destructive("remove all aliases")
        assert result is True

    def test_cancelled_returns_false(self, capsys):
        with patch("builtins.input", return_value="n"):
            result = confirm_destructive("remove all aliases")
        assert result is False

    def test_with_target_shows_warning(self, capsys):
        with patch("builtins.input", return_value="n"):
            confirm_destructive("remove", "startup commands")
        captured = capsys.readouterr()
        assert "startup commands" in captured.out

    def test_default_is_no(self, capsys):
        with patch("builtins.input", return_value=""):
            result = confirm_destructive("delete everything")
        assert result is False
