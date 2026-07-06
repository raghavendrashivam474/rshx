"""
test_environment.py
Unit tests for rshx.core.environment.
"""

import pytest
from rshx.core.environment import Environment


@pytest.fixture()
def env() -> Environment:
    return Environment()


class TestEnvironmentSet:
    def test_set_creates_variable(self, env):
        env.set("PROJECTS", "C:\\Projects")
        assert env.get("PROJECTS") == "C:\\Projects"

    def test_set_overwrites_existing(self, env):
        env.set("PROJECTS", "C:\\Projects")
        env.set("PROJECTS", "D:\\Projects")
        assert env.get("PROJECTS") == "D:\\Projects"

    def test_set_empty_name_raises(self, env):
        with pytest.raises(ValueError, match="empty"):
            env.set("", "value")

    def test_set_whitespace_name_raises(self, env):
        with pytest.raises(ValueError, match="empty"):
            env.set("   ", "value")

    def test_set_invalid_name_raises(self, env):
        with pytest.raises(ValueError, match="invalid characters"):
            env.set("MY VAR", "value")

    def test_set_name_starting_with_digit_raises(self, env):
        with pytest.raises(ValueError, match="invalid characters"):
            env.set("1VAR", "value")

    def test_set_empty_value_is_allowed(self, env):
        env.set("EMPTY", "")
        assert env.get("EMPTY") == ""

    def test_set_underscore_name_is_valid(self, env):
        env.set("_MY_VAR", "value")
        assert env.get("_MY_VAR") == "value"


class TestEnvironmentRemove:
    def test_remove_existing_variable(self, env):
        env.set("PROJECTS", "C:\\Projects")
        env.remove("PROJECTS")
        assert env.get("PROJECTS") is None

    def test_remove_nonexistent_raises(self, env):
        with pytest.raises(KeyError, match="not found"):
            env.remove("PROJECTS")


class TestEnvironmentGet:
    def test_get_returns_value(self, env):
        env.set("EDITOR", "code")
        assert env.get("EDITOR") == "code"

    def test_get_returns_none_for_missing(self, env):
        assert env.get("MISSING") is None


class TestEnvironmentExists:
    def test_exists_true_when_defined(self, env):
        env.set("EDITOR", "code")
        assert env.exists("EDITOR") is True

    def test_exists_false_when_not_defined(self, env):
        assert env.exists("EDITOR") is False


class TestEnvironmentAll:
    def test_all_returns_empty_initially(self, env):
        assert env.all() == {}

    def test_all_returns_copy(self, env):
        env.set("EDITOR", "code")
        result = env.all()
        result["EDITOR"] = "vim"
        assert env.get("EDITOR") == "code"

    def test_all_returns_all_variables(self, env):
        env.set("EDITOR", "code")
        env.set("PROJECTS", "C:\\Projects")
        result = env.all()
        assert result["EDITOR"] == "code"
        assert result["PROJECTS"] == "C:\\Projects"


class TestEnvironmentExpand:
    def test_expand_single_variable(self, env):
        env.set("NAME", "ragha")
        result, warnings = env.expand("echo %NAME%")
        assert result == "echo ragha"
        assert warnings == []

    def test_expand_multiple_variables(self, env):
        env.set("A", "hello")
        env.set("B", "world")
        result, warnings = env.expand("%A% %B%")
        assert result == "hello world"
        assert warnings == []

    def test_expand_undefined_variable_produces_warning(self, env):
        result, warnings = env.expand("cd %UNKNOWN%")
        assert "%UNKNOWN%" in result
        assert len(warnings) == 1
        assert "UNKNOWN" in warnings[0]

    def test_expand_no_variables_unchanged(self, env):
        result, warnings = env.expand("git status")
        assert result == "git status"
        assert warnings == []

    def test_expand_variable_in_path(self, env):
        env.set("PROJECTS", "C:\\Projects")
        result, warnings = env.expand("cd %PROJECTS%\\rshx")
        assert result == "cd C:\\Projects\\rshx"
        assert warnings == []

    def test_expand_empty_string(self, env):
        result, warnings = env.expand("")
        assert result == ""
        assert warnings == []

    def test_expand_mixed_defined_and_undefined(self, env):
        env.set("KNOWN", "value")
        result, warnings = env.expand("%KNOWN% %UNKNOWN%")
        assert "value" in result
        assert "%UNKNOWN%" in result
        assert len(warnings) == 1


class TestEnvironmentCount:
    def test_count_zero_initially(self, env):
        assert env.count() == 0

    def test_count_increments(self, env):
        env.set("A", "1")
        assert env.count() == 1


class TestEnvironmentClear:
    def test_clear_removes_all(self, env):
        env.set("A", "1")
        env.set("B", "2")
        env.clear()
        assert env.count() == 0
