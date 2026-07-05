"""
test_ast_parser.py
Unit tests for the Sprint 2 parser (rshx.core.parser).
"""

import pytest
from rshx.core.parser import parse
from rshx.core.ast import PipelineNode, RedirectType


class TestParseEmpty:
    def test_empty_string_returns_empty_pipeline(self):
        result = parse("")
        assert result.stage_count() == 0

    def test_whitespace_returns_empty_pipeline(self):
        result = parse("   ")
        assert result.stage_count() == 0


class TestParseSingleCommand:
    def test_single_command_name(self):
        result = parse("git")
        assert result.stage_count() == 1
        assert result.stages[0].command.name == "git"

    def test_single_command_with_args(self):
        result = parse("git status")
        stage = result.stages[0]
        assert stage.command.name == "git"
        assert stage.command.args == ["status"]

    def test_command_name_is_lowercased(self):
        result = parse("GIT status")
        assert result.stages[0].command.name == "git"


class TestParsePipeline:
    def test_two_stage_pipeline(self):
        result = parse("git status | find modified")
        assert result.stage_count() == 2
        assert result.stages[0].command.name == "git"
        assert result.stages[1].command.name == "find"

    def test_three_stage_pipeline(self):
        result = parse("a | b | c")
        assert result.stage_count() == 3
        assert result.stages[0].command.name == "a"
        assert result.stages[1].command.name == "b"
        assert result.stages[2].command.name == "c"

    def test_pipeline_args_preserved(self):
        result = parse("git log --oneline | find commit")
        assert result.stages[0].command.args == ["log", "--oneline"]
        assert result.stages[1].command.args == ["commit"]


class TestParseOutputRedirect:
    def test_output_overwrite(self):
        result = parse("dir > output.txt")
        stage = result.stages[0]
        assert stage.stdout_file == "output.txt"
        assert stage.stdout_mode == RedirectType.OUTPUT_OVERWRITE

    def test_output_append(self):
        result = parse("dir >> log.txt")
        stage = result.stages[0]
        assert stage.stdout_file == "log.txt"
        assert stage.stdout_mode == RedirectType.OUTPUT_APPEND

    def test_command_name_correct_with_redirect(self):
        result = parse("dir > out.txt")
        assert result.stages[0].command.name == "dir"


class TestParseInputRedirect:
    def test_input_redirect(self):
        result = parse("sort < names.txt")
        stage = result.stages[0]
        assert stage.stdin_file == "names.txt"

    def test_command_correct_with_input_redirect(self):
        result = parse("sort < names.txt")
        assert result.stages[0].command.name == "sort"


class TestParseCombined:
    def test_pipeline_with_output_redirect(self):
        result = parse("git status | find modified > out.txt")
        assert result.stage_count() == 2
        assert result.stages[1].stdout_file == "out.txt"
        assert result.stages[0].stdout_file is None

    def test_input_redirect_on_first_stage(self):
        result = parse("sort < input.txt | find hello")
        assert result.stages[0].stdin_file == "input.txt"
        assert result.stages[1].stdin_file is None


class TestParseSyntaxErrors:
    def test_leading_pipe_raises(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("| git status")

    def test_trailing_pipe_raises(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("git status |")

    def test_redirect_out_without_filename_raises(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("dir >")

    def test_redirect_append_without_filename_raises(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("dir >>")

    def test_redirect_in_without_filename_raises(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("sort <")

    def test_only_redirect_operator_raises(self):
        with pytest.raises(ValueError, match="Parse error"):
            parse("> output.txt")
