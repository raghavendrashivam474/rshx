"""
test_parser.py
Unit tests for rshx.core.parser - Sprint 2.

ParsedCommand no longer exists. The parser now produces PipelineNode.
Sprint 2 parser tests live in test_ast_parser.py.
This file covers the internal helpers: _tokenize and _strip_quotes.
"""

import pytest
from rshx.core.parser import parse, _tokenize, _strip_quotes
from rshx.core.ast import PipelineNode, RedirectType


class TestParseEmptyInput:
    def test_empty_string_returns_empty_pipeline(self):
        result = parse("")
        assert isinstance(result, PipelineNode)
        assert result.stage_count() == 0

    def test_whitespace_only_returns_empty_pipeline(self):
        result = parse("   ")
        assert result.stage_count() == 0


class TestParseCommandName:
    def test_single_word_sets_name(self):
        result = parse("help")
        assert result.stages[0].command.name == "help"

    def test_command_name_is_lowercased(self):
        result = parse("HELP")
        assert result.stages[0].command.name == "help"

    def test_mixed_case_command_is_lowercased(self):
        result = parse("HeLp")
        assert result.stages[0].command.name == "help"


class TestParseArguments:
    def test_no_arguments_returns_empty_list(self):
        result = parse("pwd")
        assert result.stages[0].command.args == []

    def test_single_argument_is_captured(self):
        result = parse("cd /tmp")
        assert result.stages[0].command.args == ["/tmp"]

    def test_multiple_arguments_are_captured(self):
        result = parse("git commit -m message")
        assert result.stages[0].command.args == ["commit", "-m", "message"]

    def test_quoted_argument_is_single_token(self):
        result = parse('git commit -m "my commit message"')
        assert result.stages[0].command.args == ["commit", "-m", "my commit message"]


class TestParseWindowsPaths:
    def test_backslash_path_is_preserved(self):
        result = parse(r"cd C:\Users\ragha")
        assert r"C:\Users\ragha" in result.stages[0].command.args[0]

    def test_absolute_windows_path(self):
        result = parse(r"cd C:\Users\ragha\Documents")
        assert "Documents" in result.stages[0].command.args[0]


class TestParseRaw:
    def test_raw_pipeline_has_correct_stage_count(self):
        result = parse("git status | find modified")
        assert result.stage_count() == 2


class TestParseErrors:
    def test_mismatched_quotes_raise_value_error(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("echo 'unclosed")

    def test_trailing_pipe_raises_value_error(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("git status |")

    def test_leading_pipe_raises_value_error(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("| git status")

    def test_redirect_without_filename_raises(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("dir >")


class TestTokenize:
    def test_simple_command_tokenized(self):
        tokens = _tokenize("git status")
        assert tokens == ["git", "status"]

    def test_pipe_becomes_separate_token(self):
        tokens = _tokenize("git status | find modified")
        assert "|" in tokens

    def test_redirect_out_becomes_token(self):
        tokens = _tokenize("dir > out.txt")
        assert ">" in tokens
        assert "out.txt" in tokens

    def test_redirect_append_becomes_token(self):
        tokens = _tokenize("dir >> log.txt")
        assert ">>" in tokens
        assert "log.txt" in tokens

    def test_redirect_in_becomes_token(self):
        tokens = _tokenize("sort < names.txt")
        assert "<" in tokens
        assert "names.txt" in tokens


class TestStripQuotes:
    def test_strips_double_quotes(self):
        assert _strip_quotes('"hello"') == "hello"

    def test_strips_single_quotes(self):
        assert _strip_quotes("'hello'") == "hello"

    def test_no_quotes_unchanged(self):
        assert _strip_quotes("hello") == "hello"

    def test_single_char_unchanged(self):
        assert _strip_quotes("h") == "h"

    def test_mismatched_quotes_unchanged(self):
        assert _strip_quotes("\"hello'") == "\"hello'"
