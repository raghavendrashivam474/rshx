"""
test_script_parser.py
Unit tests for rshx.core.script_parser.
"""

import pytest
from rshx.core.script_parser import parse_script
from rshx.core.script_types import ScriptNode


class TestParseBasic:
    def test_empty_source_returns_empty_node(self):
        node, errors = parse_script("")
        assert node.is_empty()
        assert errors == []

    def test_blank_lines_ignored(self):
        source = "\n\n\npwd\n\n\ngit status\n\n"
        node, errors = parse_script(source)
        assert node.command_count() == 2
        assert errors == []

    def test_comments_ignored(self):
        source = "# This is a comment\npwd\n# Another comment\ngit status"
        node, errors = parse_script(source)
        assert node.command_count() == 2
        assert errors == []

    def test_command_source_preserved(self):
        node, errors = parse_script("git log --oneline")
        assert node.commands[0].source == "git log --oneline"

    def test_line_numbers_preserved(self):
        source = "# comment\n\npwd\ngit status"
        node, _ = parse_script(source)
        assert node.commands[0].line_number == 3
        assert node.commands[1].line_number == 4

    def test_multiple_commands(self):
        source = "pwd\nwhoami\ngit status"
        node, _ = parse_script(source)
        assert node.command_count() == 3


class TestParseDirectives:
    def test_name_directive(self):
        node, errors = parse_script("@name My Script\npwd")
        assert node.name == "My Script"
        assert errors == []

    def test_description_directive(self):
        node, errors = parse_script("@description Does things\npwd")
        assert node.description == "Does things"
        assert errors == []

    def test_continue_on_error_true(self):
        node, errors = parse_script("@continue_on_error true\npwd")
        assert node.continue_on_error is True
        assert errors == []

    def test_continue_on_error_false(self):
        node, errors = parse_script("@continue_on_error false\npwd")
        assert node.continue_on_error is False
        assert errors == []

    def test_continue_on_error_case_insensitive(self):
        node, errors = parse_script("@continue_on_error TRUE\npwd")
        assert node.continue_on_error is True

    def test_invalid_continue_on_error_value_produces_error(self):
        node, errors = parse_script("@continue_on_error maybe\npwd")
        assert len(errors) > 0
        assert any("continue_on_error" in e.message for e in errors)

    def test_unknown_directive_produces_error(self):
        node, errors = parse_script("@unknown value\npwd")
        assert len(errors) > 0
        assert any("Unknown directive" in e.message for e in errors)

    def test_empty_directive_produces_error(self):
        node, errors = parse_script("@\npwd")
        assert len(errors) > 0

    def test_directives_stored_in_node(self):
        node, _ = parse_script("@name Test\n@description Hello\npwd")
        assert len(node.directives) == 2

    def test_all_directives_together(self):
        source = "@name Full Script\n@description All directives\n@continue_on_error true\npwd"
        node, errors = parse_script(source)
        assert node.name == "Full Script"
        assert node.description == "All directives"
        assert node.continue_on_error is True
        assert node.command_count() == 1
        assert errors == []

    def test_script_path_in_errors(self):
        _, errors = parse_script("@continue_on_error bad", script_path="test.rshx")
        assert any("test.rshx" in e.script_path for e in errors)

    def test_line_number_in_errors(self):
        _, errors = parse_script("\n\n@continue_on_error bad", script_path="test.rshx")
        assert any(e.line_number == 3 for e in errors)


class TestParsePipelines:
    def test_pipeline_command_preserved(self):
        node, _ = parse_script("git log --oneline | find feat")
        assert "|" in node.commands[0].source

    def test_redirect_command_preserved(self):
        node, _ = parse_script("git status > status.txt")
        assert ">" in node.commands[0].source
