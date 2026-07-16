"""
test_command_queue.py
---------------------
Unit tests for rshx.core.command_queue.

Tests cover:
- CommandResult structure
- QueueResult aggregation methods
- Single command execution
- Multi-command sequential execution
- Stop-on-failure behaviour
- Continue-on-failure behaviour
- KeyboardInterrupt handling
- Shell state running=False halts queue
- Empty command list
- Preprocessor warnings forwarded
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, call

from rshx.core.command_queue import CommandQueue, CommandResult, QueueResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_preprocessor():
    """Preprocessor that returns input unchanged with no warnings."""
    preprocessor = MagicMock()
    preprocessor.process.side_effect = lambda cmd: (cmd, [])
    return preprocessor


@pytest.fixture()
def mock_state():
    """Minimal shell state with running=True."""
    state = MagicMock()
    state.running = True
    return state


@pytest.fixture()
def queue(mock_preprocessor, mock_state):
    """CommandQueue with default stop_on_failure=True."""
    return CommandQueue(
        preprocessor=mock_preprocessor,
        shell_state=mock_state,
    )


@pytest.fixture()
def queue_continue(mock_preprocessor, mock_state):
    """CommandQueue with stop_on_failure=False."""
    return CommandQueue(
        preprocessor=mock_preprocessor,
        shell_state=mock_state,
        stop_on_failure=False,
    )


# ---------------------------------------------------------------------------
# CommandResult
# ---------------------------------------------------------------------------

class TestCommandResult:
    def test_successful_result(self):
        result = CommandResult(command="pwd", success=True)
        assert result.command == "pwd"
        assert result.success is True
        assert result.interrupted is False
        assert result.error is None

    def test_failed_result_with_error(self):
        result = CommandResult(command="bad", success=False, error="Parse failed")
        assert result.success is False
        assert result.error == "Parse failed"
        assert result.interrupted is False

    def test_interrupted_result(self):
        result = CommandResult(command="sleep 10", success=False, interrupted=True)
        assert result.interrupted is True
        assert result.success is False
        assert result.error is None


# ---------------------------------------------------------------------------
# QueueResult
# ---------------------------------------------------------------------------

class TestQueueResult:
    def test_empty_result(self):
        result = QueueResult()
        assert result.total() == 0
        assert result.succeeded() == 0
        assert result.failed() == 0
        assert result.was_interrupted() is False
        assert result.all_succeeded() is False
        assert result.stopped_early is False

    def test_all_succeeded(self):
        result = QueueResult(results=[
            CommandResult(command="pwd", success=True),
            CommandResult(command="git status", success=True),
        ])
        assert result.total() == 2
        assert result.succeeded() == 2
        assert result.failed() == 0
        assert result.all_succeeded() is True
        assert result.was_interrupted() is False

    def test_one_failed(self):
        result = QueueResult(results=[
            CommandResult(command="pwd", success=True),
            CommandResult(command="bad", success=False, error="err"),
        ])
        assert result.succeeded() == 1
        assert result.failed() == 1
        assert result.all_succeeded() is False

    def test_interrupted_detected(self):
        result = QueueResult(results=[
            CommandResult(command="pwd", success=True),
            CommandResult(command="long", success=False, interrupted=True),
        ])
        assert result.was_interrupted() is True
        assert result.failed() == 0

    def test_stopped_early_flag(self):
        result = QueueResult(stopped_early=True)
        assert result.stopped_early is True

    def test_failed_does_not_count_interrupted(self):
        result = QueueResult(results=[
            CommandResult(command="a", success=False, interrupted=True),
            CommandResult(command="b", success=False, error="boom"),
        ])
        assert result.failed() == 1
        assert result.was_interrupted() is True


# ---------------------------------------------------------------------------
# Empty queue
# ---------------------------------------------------------------------------

class TestEmptyQueue:
    def test_empty_list_returns_empty_result(self, queue):
        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute") as mock_execute:
            result = queue.run([])
            assert result.total() == 0
            assert result.stopped_early is False
            mock_parse.assert_not_called()
            mock_execute.assert_not_called()


# ---------------------------------------------------------------------------
# Single command
# ---------------------------------------------------------------------------

class TestSingleCommand:
    def test_single_command_succeeds(self, queue, mock_preprocessor):
        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute") as mock_execute:
            result = queue.run(["pwd"])
            assert result.total() == 1
            assert result.succeeded() == 1
            assert result.all_succeeded() is True
            assert result.stopped_early is False
            mock_preprocessor.process.assert_called_once_with("pwd")
            mock_parse.assert_called_once()
            mock_execute.assert_called_once()

    def test_single_command_result_command_stored(self, queue):
        with patch("rshx.core.command_queue.parse"), \
             patch("rshx.core.command_queue.execute"):
            result = queue.run(["git status"])
            assert result.results[0].command == "git status"

    def test_single_command_preprocessor_expansion_used(self, mock_preprocessor, mock_state):
        mock_preprocessor.process.side_effect = lambda cmd: ("expanded_cmd", [])
        queue = CommandQueue(
            preprocessor=mock_preprocessor,
            shell_state=mock_state,
        )
        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            queue.run(["original"])
            args, _ = mock_parse.call_args
            assert args[0] == "expanded_cmd"


# ---------------------------------------------------------------------------
# Multi-command execution
# ---------------------------------------------------------------------------

class TestMultiCommand:
    def test_two_commands_both_executed(self, queue, mock_preprocessor):
        with patch("rshx.core.command_queue.parse"), \
             patch("rshx.core.command_queue.execute"):
            result = queue.run(["pwd", "git status"])
            assert result.total() == 2
            assert result.succeeded() == 2
            assert mock_preprocessor.process.call_count == 2

    def test_five_commands_all_executed(self, queue, mock_preprocessor):
        commands = ["a", "b", "c", "d", "e"]
        with patch("rshx.core.command_queue.parse"), \
             patch("rshx.core.command_queue.execute"):
            result = queue.run(commands)
            assert result.total() == 5
            assert result.succeeded() == 5

    def test_commands_executed_in_order(self, mock_preprocessor, mock_state):
        execution_order = []
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        queue = CommandQueue(
            preprocessor=mock_preprocessor,
            shell_state=mock_state,
        )

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = lambda cmd: execution_order.append(cmd) or MagicMock()
            queue.run(["first", "second", "third"])

        assert execution_order == ["first", "second", "third"]


# ---------------------------------------------------------------------------
# Stop on failure
# ---------------------------------------------------------------------------

class TestStopOnFailure:
    def test_stops_after_first_failure(self, queue, mock_preprocessor):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = [Exception("parse error"), MagicMock()]
            result = queue.run(["bad", "good"])

        assert result.total() == 1
        assert result.failed() == 1
        assert result.stopped_early is True

    def test_stopped_early_true_when_commands_remain(self, queue, mock_preprocessor):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = Exception("boom")
            result = queue.run(["bad", "skipped", "also_skipped"])

        assert result.stopped_early is True
        assert result.total() == 1

    def test_stopped_early_false_when_last_command_fails(self, queue, mock_preprocessor):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = [MagicMock(), Exception("last fails")]
            result = queue.run(["good", "bad"])

        assert result.total() == 2
        assert result.stopped_early is False

    def test_error_message_stored_in_result(self, queue, mock_preprocessor):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = Exception("specific error message")
            result = queue.run(["bad"])

        assert result.results[0].error == "specific error message"
        assert result.results[0].success is False


# ---------------------------------------------------------------------------
# Continue on failure
# ---------------------------------------------------------------------------

class TestContinueOnFailure:
    def test_continues_after_failure(self, queue_continue, mock_preprocessor):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = [Exception("fail"), MagicMock()]
            result = queue_continue.run(["bad", "good"])

        assert result.total() == 2
        assert result.failed() == 1
        assert result.succeeded() == 1

    def test_all_three_run_despite_middle_failure(self, queue_continue, mock_preprocessor):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = [MagicMock(), Exception("middle"), MagicMock()]
            result = queue_continue.run(["a", "bad", "c"])

        assert result.total() == 3
        assert result.succeeded() == 2
        assert result.failed() == 1
        assert result.stopped_early is False


# ---------------------------------------------------------------------------
# KeyboardInterrupt
# ---------------------------------------------------------------------------

class TestKeyboardInterrupt:
    def test_interrupt_stops_queue(self, queue, mock_preprocessor):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = [KeyboardInterrupt(), MagicMock()]
            result = queue.run(["interrupted", "skipped"])

        assert result.total() == 1
        assert result.was_interrupted() is True
        assert result.stopped_early is True

    def test_interrupt_result_marked_correctly(self, queue, mock_preprocessor):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = KeyboardInterrupt()
            result = queue.run(["cmd"])

        assert result.results[0].interrupted is True
        assert result.results[0].success is False
        assert result.results[0].error is None

    def test_interrupt_always_halts_even_with_continue_on_failure(
        self, queue_continue, mock_preprocessor
    ):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, [])

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute"):
            mock_parse.side_effect = [KeyboardInterrupt(), MagicMock()]
            result = queue_continue.run(["interrupted", "skipped"])

        assert result.total() == 1
        assert result.was_interrupted() is True


# ---------------------------------------------------------------------------
# Shell state running=False
# ---------------------------------------------------------------------------

class TestShellStateRunning:
    def test_queue_stops_when_running_false(self, mock_preprocessor, mock_state):
        mock_state.running = False
        queue = CommandQueue(
            preprocessor=mock_preprocessor,
            shell_state=mock_state,
        )

        with patch("rshx.core.command_queue.parse") as mock_parse, \
             patch("rshx.core.command_queue.execute") as mock_execute:
            result = queue.run(["pwd", "git status"])

        assert result.total() == 0
        assert result.stopped_early is True
        mock_parse.assert_not_called()
        mock_execute.assert_not_called()

    def test_queue_stops_mid_run_when_running_set_false(
        self, mock_preprocessor, mock_state
    ):
        calls = []

        def set_running_false(cmd):
            calls.append(cmd)
            if cmd == "exit":
                mock_state.running = False
            return (cmd, [])

        mock_preprocessor.process.side_effect = set_running_false

        queue = CommandQueue(
            preprocessor=mock_preprocessor,
            shell_state=mock_state,
        )

        with patch("rshx.core.command_queue.parse"), \
             patch("rshx.core.command_queue.execute"):
            result = queue.run(["pwd", "exit", "git status"])

        assert "git status" not in calls
        assert result.stopped_early is True


# ---------------------------------------------------------------------------
# Preprocessor warnings
# ---------------------------------------------------------------------------

class TestPreprocessorWarnings:
    def test_warnings_do_not_cause_failure(self, mock_preprocessor, mock_state):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, ["warning: something"])

        queue = CommandQueue(
            preprocessor=mock_preprocessor,
            shell_state=mock_state,
        )

        with patch("rshx.core.command_queue.parse"), \
             patch("rshx.core.command_queue.execute"), \
             patch("rshx.core.command_queue.print_warning") as mock_warn:
            result = queue.run(["cmd"])

        assert result.succeeded() == 1
        mock_warn.assert_called_once_with("warning: something")

    def test_multiple_warnings_all_forwarded(self, mock_preprocessor, mock_state):
        mock_preprocessor.process.side_effect = lambda cmd: (cmd, ["w1", "w2", "w3"])

        queue = CommandQueue(
            preprocessor=mock_preprocessor,
            shell_state=mock_state,
        )

        with patch("rshx.core.command_queue.parse"), \
             patch("rshx.core.command_queue.execute"), \
             patch("rshx.core.command_queue.print_warning") as mock_warn:
            result = queue.run(["cmd"])

        assert mock_warn.call_count == 3