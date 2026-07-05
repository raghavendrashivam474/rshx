"""
test_ast.py
Unit tests for rshx.core.ast.
"""

from rshx.core.ast import (
    CommandNode,
    RedirectNode,
    PipelineNode,
    RedirectType,
)


class TestCommandNode:
    def test_name_is_stored(self):
        cmd = CommandNode(name="git")
        assert cmd.name == "git"

    def test_args_default_empty(self):
        cmd = CommandNode(name="git")
        assert cmd.args == []

    def test_args_are_stored(self):
        cmd = CommandNode(name="git", args=["status"])
        assert cmd.args == ["status"]

    def test_is_empty_true_when_name_blank(self):
        cmd = CommandNode(name="")
        assert cmd.is_empty()

    def test_is_empty_false_when_name_present(self):
        cmd = CommandNode(name="git")
        assert not cmd.is_empty()

    def test_to_argv_single_command(self):
        cmd = CommandNode(name="git")
        assert cmd.to_argv() == ["git"]

    def test_to_argv_with_args(self):
        cmd = CommandNode(name="git", args=["commit", "-m", "msg"])
        assert cmd.to_argv() == ["git", "commit", "-m", "msg"]


class TestRedirectNode:
    def test_defaults_have_no_redirections(self):
        node = RedirectNode(command=CommandNode(name="ls"))
        assert not node.has_stdin_redirect()
        assert not node.has_stdout_redirect()

    def test_stdin_redirect_detected(self):
        node = RedirectNode(
            command=CommandNode(name="sort"),
            stdin_file="input.txt",
        )
        assert node.has_stdin_redirect()

    def test_stdout_redirect_detected(self):
        node = RedirectNode(
            command=CommandNode(name="dir"),
            stdout_file="out.txt",
            stdout_mode=RedirectType.OUTPUT_OVERWRITE,
        )
        assert node.has_stdout_redirect()

    def test_no_stdin_when_none(self):
        node = RedirectNode(command=CommandNode(name="ls"), stdin_file=None)
        assert not node.has_stdin_redirect()

    def test_no_stdout_when_none(self):
        node = RedirectNode(command=CommandNode(name="ls"), stdout_file=None)
        assert not node.has_stdout_redirect()


class TestPipelineNode:
    def test_empty_pipeline(self):
        p = PipelineNode(stages=[])
        assert p.stage_count() == 0

    def test_single_stage(self):
        stage = RedirectNode(command=CommandNode(name="ls"))
        p = PipelineNode(stages=[stage])
        assert p.is_single_command()
        assert p.stage_count() == 1

    def test_multi_stage(self):
        stages = [
            RedirectNode(command=CommandNode(name="ls")),
            RedirectNode(command=CommandNode(name="find")),
        ]
        p = PipelineNode(stages=stages)
        assert not p.is_single_command()
        assert p.stage_count() == 2

    def test_stage_count_three(self):
        stages = [
            RedirectNode(command=CommandNode(name="a")),
            RedirectNode(command=CommandNode(name="b")),
            RedirectNode(command=CommandNode(name="c")),
        ]
        p = PipelineNode(stages=stages)
        assert p.stage_count() == 3
