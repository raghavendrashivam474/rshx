"""
test_preprocessor.py
Unit tests for rshx.core.preprocessor.
"""

import pytest
from rshx.core.alias_manager import AliasManager
from rshx.core.environment import Environment
from rshx.core.preprocessor import Preprocessor


@pytest.fixture()
def alias_mgr() -> AliasManager:
    return AliasManager()


@pytest.fixture()
def env() -> Environment:
    return Environment()


@pytest.fixture()
def preprocessor(alias_mgr, env) -> Preprocessor:
    return Preprocessor(alias_manager=alias_mgr, environment=env)


class TestPreprocessorEmpty:
    def test_empty_input_returns_empty(self, preprocessor):
        result, warnings = preprocessor.process("")
        assert result == ""
        assert warnings == []

    def test_whitespace_only_returns_empty(self, preprocessor):
        result, warnings = preprocessor.process("   ")
        assert result == ""
        assert warnings == []


class TestPreprocessorAliasExpansion:
    def test_alias_expands_first_token(self, preprocessor, alias_mgr):
        alias_mgr.set("gs", "git status")
        result, warnings = preprocessor.process("gs")
        assert result == "git status"
        assert warnings == []

    def test_alias_preserves_arguments(self, preprocessor, alias_mgr):
        alias_mgr.set("gs", "git status")
        result, warnings = preprocessor.process("gs --short")
        assert result == "git status --short"
        assert warnings == []

    def test_no_alias_match_returns_original(self, preprocessor):
        result, warnings = preprocessor.process("git status")
        assert result == "git status"
        assert warnings == []

    def test_alias_only_expands_first_token(self, preprocessor, alias_mgr):
        alias_mgr.set("gs", "git status")
        result, warnings = preprocessor.process("echo gs")
        assert result == "echo gs"

    def test_alias_with_pipeline(self, preprocessor, alias_mgr):
        alias_mgr.set("gs", "git status")
        result, warnings = preprocessor.process("gs | find modified")
        assert result == "git status | find modified"


class TestPreprocessorVariableExpansion:
    def test_variable_expands(self, preprocessor, env):
        env.set("PROJECTS", "C:\\Projects")
        result, warnings = preprocessor.process("cd %PROJECTS%")
        assert result == "cd C:\\Projects"
        assert warnings == []

    def test_undefined_variable_produces_warning(self, preprocessor):
        result, warnings = preprocessor.process("cd %UNKNOWN%")
        assert "%UNKNOWN%" in result
        assert len(warnings) == 1

    def test_multiple_variables_expand(self, preprocessor, env):
        env.set("A", "hello")
        env.set("B", "world")
        result, warnings = preprocessor.process("echo %A% %B%")
        assert result == "echo hello world"
        assert warnings == []


class TestPreprocessorCombined:
    def test_alias_then_variable_expansion(self, preprocessor, alias_mgr, env):
        alias_mgr.set("goto", "cd")
        env.set("PROJECTS", "C:\\Projects")
        result, warnings = preprocessor.process("goto %PROJECTS%")
        assert result == "cd C:\\Projects"
        assert warnings == []

    def test_no_expansion_needed(self, preprocessor):
        result, warnings = preprocessor.process("git log --oneline")
        assert result == "git log --oneline"
        assert warnings == []

    def test_alias_in_pipeline_with_variable(self, preprocessor, alias_mgr, env):
        alias_mgr.set("gs", "git status")
        env.set("TERM", "modified")
        result, warnings = preprocessor.process("gs | find %TERM%")
        assert result == "git status | find modified"
        assert warnings == []

    def test_whitespace_stripped_from_input(self, preprocessor, alias_mgr):
        alias_mgr.set("gs", "git status")
        result, warnings = preprocessor.process("  gs  ")
        assert result == "git status"
