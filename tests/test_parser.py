"""
test_parser.py
Unit tests for rshx.core.parser.
"""

import pytest
from rshx.core.parser import parse, ParsedCommand


class TestParseEmptyInput:
    def test_empty_string_returns_empty_command(self):
        result = parse("")
        assert result.is_empty()

    def test_whitespace_only_returns_empty_command(self):
        result = parse("   ")
        assert result.is_empty()


class TestParseCommandName:
    def test_single_word_sets_name(self):
        result = parse("help")
        assert result.name == "help"

    def test_command_name_is_lowercased(self):
        result = parse("HELP")
        assert result.name == "help"

    def test_mixed_case_command_is_lowercased(self):
        result = parse("HeLp")
        assert result.name == "help"


class TestParseArguments:
    def test_no_arguments_returns_empty_list(self):
        result = parse("pwd")
        assert result.args == []

    def test_single_argument_is_captured(self):
        result = parse("cd /tmp")
        assert result.args == ["/tmp"]

    def test_multiple_arguments_are_captured(self):
        result = parse("git commit -m message")
        assert result.args == ["commit", "-m", "message"]

    def test_quoted_argument_is_single_token(self):
        result = parse('git commit -m "my commit message"')
        assert result.args == ["commit", "-m", "my commit message"]


class TestParseRaw:
    def test_raw_input_is_preserved(self):
        raw = "  cd /some/path  "
        result = parse(raw)
        assert result.raw == raw


class TestParseErrors:
    def test_mismatched_quotes_raise_value_error(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("echo 'unclosed")
