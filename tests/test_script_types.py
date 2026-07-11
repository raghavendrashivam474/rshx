"""
test_script_types.py
Unit tests for rshx.core.script_types.
"""

import pytest
from rshx.core.script_types import (
    ScriptCommand,
    ScriptDirective,
    ScriptNode,
    ScriptError,
    ScriptResult,
)


class TestScriptCommand:
    def test_stores_source_and_line(self):
        cmd = ScriptCommand(source="git status", line_number=5)
        assert cmd.source == "git status"
        assert cmd.line_number == 5


class TestScriptDirective:
    def test_stores_key_value_line(self):
        d = ScriptDirective(key="name", value="My Script", line_number=1)
        assert d.key == "name"
        assert d.value == "My Script"
        assert d.line_number == 1


class TestScriptNode:
    def test_defaults(self):
        node = ScriptNode(path="/tmp/test.rshx")
        assert node.name == ""
        assert node.description == ""
        assert node.continue_on_error is False
        assert node.commands == []
        assert node.directives == []

    def test_command_count(self):
        node = ScriptNode(path="x.rshx")
        node.commands.append(ScriptCommand(source="pwd", line_number=1))
        assert node.command_count() == 1

    def test_is_empty_true(self):
        node = ScriptNode(path="x.rshx")
        assert node.is_empty() is True

    def test_is_empty_false(self):
        node = ScriptNode(path="x.rshx")
        node.commands.append(ScriptCommand(source="pwd", line_number=1))
        assert node.is_empty() is False


class TestScriptError:
    def test_format_minimal(self):
        err = ScriptError(message="Something failed")
        assert "Something failed" in err.format()

    def test_format_full(self):
        err = ScriptError(
            message="Command failed",
            script_path="test.rshx",
            line_number=5,
            command="pytest",
            exit_code=1,
        )
        formatted = err.format()
        assert "Command failed" in formatted
        assert "test.rshx" in formatted
        assert "5" in formatted
        assert "pytest" in formatted
        assert "1" in formatted

    def test_format_no_optional_fields(self):
        err = ScriptError(message="oops")
        formatted = err.format()
        assert "File" not in formatted
        assert "Line" not in formatted


class TestScriptResult:
    def test_defaults(self):
        r = ScriptResult(script_name="test", script_path="test.rshx")
        assert r.success is True
        assert r.errors == []
        assert r.commands_failed == 0

    def test_add_error_marks_failed(self):
        r = ScriptResult(script_name="test", script_path="test.rshx")
        err = ScriptError(message="oops")
        r.add_error(err)
        assert r.success is False
        assert r.commands_failed == 1
        assert len(r.errors) == 1

    def test_multiple_errors(self):
        r = ScriptResult(script_name="test", script_path="test.rshx")
        r.add_error(ScriptError(message="first"))
        r.add_error(ScriptError(message="second"))
        assert r.commands_failed == 2
        assert len(r.errors) == 2
