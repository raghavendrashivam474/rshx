"""
test_parser.py
Unit tests for rshx.core.parser - Sprint 2.
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

    def test_quoted_argument_preserves_quotes_for_external_commands(self):
        """
        Quoted arguments intentionally preserve their quotes so that
        external commands such as Windows find receive correctly quoted
        arguments e.g. find "feat" not find feat.
        """
        result = parse('git commit -m "my commit message"')
        args = result.stages[0].command.args
        assert "commit" in args
        assert "-m" in args
        # Quote is preserved in the argument token
        assert any("my commit message" in arg for arg in args)

    def test_quoted_find_argument_preserves_quotes(self):
        """find 'feat' on Windows requires the quotes to be preserved."""
        result = parse('find "feat"')
        args = result.stages[0].command.args
        assert len(args) == 1
        assert "feat" in args[0]


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
        assert "git" in tokens
        assert "status" in tokens

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
