"""
test_input_dispatcher.py
Unit tests for rshx.core.input_dispatcher.
"""

import pytest
from rshx.core.input_dispatcher import InputDispatcher, InputType, DispatchResult


@pytest.fixture()
def dispatcher() -> InputDispatcher:
    return InputDispatcher()


class TestDispatchEmpty:
    def test_empty_string_returns_empty(self, dispatcher):
        result = dispatcher.dispatch("")
        assert result.input_type == InputType.EMPTY
        assert result.commands == []
        assert result.is_empty() is True

    def test_whitespace_only_returns_empty(self, dispatcher):
        result = dispatcher.dispatch("   ")
        assert result.input_type == InputType.EMPTY
        assert result.is_empty() is True

    def test_newlines_only_returns_empty(self, dispatcher):
        result = dispatcher.dispatch("\n\n\n")
        assert result.input_type == InputType.EMPTY

    def test_mixed_whitespace_returns_empty(self, dispatcher):
        result = dispatcher.dispatch("  \n  \n  ")
        assert result.input_type == InputType.EMPTY

    def test_lines_with_only_spaces_returns_empty(self, dispatcher):
        """
        Covers input_dispatcher.py line 107.
        Input has content but all lines are whitespace-only.
        _extract_commands is called and returns empty list.
        """
        raw = "   \n   \n   "
        result = dispatcher.dispatch(raw)
        assert result.input_type == InputType.EMPTY
        assert result.commands == []


class TestDispatchSingle:
    def test_single_command_classified_correctly(self, dispatcher):
        result = dispatcher.dispatch("git status")
        assert result.input_type == InputType.SINGLE
        assert result.commands == ["git status"]
        assert result.command_count() == 1

    def test_single_command_whitespace_stripped(self, dispatcher):
        result = dispatcher.dispatch("  pwd  ")
        assert result.commands == ["pwd"]

    def test_single_command_with_arguments(self, dispatcher):
        result = dispatcher.dispatch("git log --oneline -5")
        assert result.input_type == InputType.SINGLE
        assert result.commands == ["git log --oneline -5"]

    def test_single_command_with_pipe(self, dispatcher):
        result = dispatcher.dispatch("git log | find feat")
        assert result.input_type == InputType.SINGLE
        assert result.commands == ["git log | find feat"]

    def test_single_command_with_redirect(self, dispatcher):
        result = dispatcher.dispatch("git status > out.txt")
        assert result.input_type == InputType.SINGLE


class TestDispatchMulti:
    def test_two_commands_classified_as_multi(self, dispatcher):
        result = dispatcher.dispatch("git add .\ngit commit -m msg")
        assert result.input_type == InputType.MULTI
        assert result.command_count() == 2
        assert result.commands[0] == "git add ."
        assert result.commands[1] == "git commit -m msg"

    def test_blank_lines_between_commands_ignored(self, dispatcher):
        result = dispatcher.dispatch("git add .\n\ngit status\n\ngit push")
        assert result.input_type == InputType.MULTI
        assert result.command_count() == 3
        assert result.commands == ["git add .", "git status", "git push"]

    def test_order_preserved(self, dispatcher):
        commands = ["pwd", "whoami", "git status", "python --version"]
        raw = "\n".join(commands)
        result = dispatcher.dispatch(raw)
        assert result.commands == commands

    def test_five_pasted_commands(self, dispatcher):
        raw = "git add .\ngit status\ngit commit -m update\ngit push\ngit log --oneline"
        result = dispatcher.dispatch(raw)
        assert result.command_count() == 5
        assert result.input_type == InputType.MULTI

    def test_whitespace_stripped_from_each_command(self, dispatcher):
        result = dispatcher.dispatch("  pwd  \n  git status  ")
        assert result.commands == ["pwd", "git status"]

    def test_trailing_newline_ignored(self, dispatcher):
        result = dispatcher.dispatch("pwd\ngit status\n")
        assert result.command_count() == 2

    def test_windows_crlf_line_endings(self, dispatcher):
        result = dispatcher.dispatch("pwd\r\ngit status\r\n")
        assert result.command_count() == 2
        assert result.commands == ["pwd", "git status"]


class TestDispatchResult:
    def test_is_empty_true_when_no_commands(self, dispatcher):
        result = dispatcher.dispatch("")
        assert result.is_empty() is True

    def test_is_empty_false_when_commands_present(self, dispatcher):
        result = dispatcher.dispatch("pwd")
        assert result.is_empty() is False

    def test_command_count_zero_for_empty(self, dispatcher):
        result = dispatcher.dispatch("")
        assert result.command_count() == 0

    def test_command_count_correct_for_multi(self, dispatcher):
        result = dispatcher.dispatch("a\nb\nc")
        assert result.command_count() == 3
