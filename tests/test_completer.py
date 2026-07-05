"""
test_completer.py
Unit tests for rshx.core.completer.
"""

import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.completion import CompleteEvent

from rshx.core.completer import BuiltinCompleter, RshxCompleter
from rshx.commands.builtins import BUILTIN_REGISTRY


def get_completions(completer, text: str) -> list[str]:
    """Helper - return completion texts for a given input string."""
    document = Document(text, cursor_position=len(text))
    event = CompleteEvent()
    return [c.text for c in completer.get_completions(document, event)]


class TestBuiltinCompleter:
    def setup_method(self):
        self.completer = BuiltinCompleter()

    def test_completes_full_command_name(self):
        results = get_completions(self.completer, "help")
        assert "help" in results

    def test_completes_partial_command(self):
        results = get_completions(self.completer, "he")
        assert "help" in results

    def test_does_not_complete_nonmatching_prefix(self):
        results = get_completions(self.completer, "xyz")
        assert results == []

    def test_completes_all_builtins_on_empty_input(self):
        results = get_completions(self.completer, "")
        for name in BUILTIN_REGISTRY:
            assert name in results

    def test_completion_includes_display_meta(self):
        document = Document("he", cursor_position=2)
        event = CompleteEvent()
        completions = list(self.completer.get_completions(document, event))
        for c in completions:
            assert c.display_meta_text == "built-in"

    def test_cl_completes_to_clear(self):
        results = get_completions(self.completer, "cl")
        assert "clear" in results

    def test_ex_completes_to_exit(self):
        results = get_completions(self.completer, "ex")
        assert "exit" in results

    def test_pw_completes_to_pwd(self):
        results = get_completions(self.completer, "pw")
        assert "pwd" in results

    def test_cd_completes_to_cd(self):
        results = get_completions(self.completer, "cd")
        assert "cd" in results


class TestRshxCompleter:
    def setup_method(self):
        self.completer = RshxCompleter()

    def test_first_token_triggers_builtin_completion(self):
        results = get_completions(self.completer, "he")
        assert "help" in results

    def test_second_token_does_not_return_builtin_completions(self):
        results = get_completions(self.completer, "cd ")
        assert "help" not in results
        assert "clear" not in results

    def test_empty_input_returns_all_builtins(self):
        results = get_completions(self.completer, "")
        for name in BUILTIN_REGISTRY:
            assert name in results
