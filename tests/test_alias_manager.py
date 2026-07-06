"""
test_alias_manager.py
Unit tests for rshx.core.alias_manager.
"""

import pytest
from rshx.core.alias_manager import AliasManager


@pytest.fixture()
def mgr() -> AliasManager:
    return AliasManager()


class TestAliasManagerSet:
    def test_set_creates_alias(self, mgr):
        mgr.set("gs", "git status")
        assert mgr.get("gs") == "git status"

    def test_set_overwrites_existing_alias(self, mgr):
        mgr.set("gs", "git status")
        mgr.set("gs", "git status --short")
        assert mgr.get("gs") == "git status --short"

    def test_set_empty_name_raises(self, mgr):
        with pytest.raises(ValueError, match="empty"):
            mgr.set("", "git status")

    def test_set_whitespace_name_raises(self, mgr):
        with pytest.raises(ValueError, match="empty"):
            mgr.set("   ", "git status")

    def test_set_name_with_space_raises(self, mgr):
        with pytest.raises(ValueError, match="whitespace"):
            mgr.set("g s", "git status")

    def test_set_empty_value_raises(self, mgr):
        with pytest.raises(ValueError, match="empty"):
            mgr.set("gs", "")

    def test_set_whitespace_value_raises(self, mgr):
        with pytest.raises(ValueError, match="empty"):
            mgr.set("gs", "   ")


class TestAliasManagerRemove:
    def test_remove_existing_alias(self, mgr):
        mgr.set("gs", "git status")
        mgr.remove("gs")
        assert mgr.get("gs") is None

    def test_remove_nonexistent_alias_raises(self, mgr):
        with pytest.raises(KeyError, match="not found"):
            mgr.remove("gs")


class TestAliasManagerGet:
    def test_get_returns_value(self, mgr):
        mgr.set("ll", "dir")
        assert mgr.get("ll") == "dir"

    def test_get_returns_none_for_missing(self, mgr):
        assert mgr.get("missing") is None


class TestAliasManagerExists:
    def test_exists_true_when_registered(self, mgr):
        mgr.set("gs", "git status")
        assert mgr.exists("gs") is True

    def test_exists_false_when_not_registered(self, mgr):
        assert mgr.exists("gs") is False


class TestAliasManagerAll:
    def test_all_returns_empty_dict_initially(self, mgr):
        assert mgr.all() == {}

    def test_all_returns_copy(self, mgr):
        mgr.set("gs", "git status")
        result = mgr.all()
        result["gs"] = "modified"
        assert mgr.get("gs") == "git status"

    def test_all_returns_all_aliases(self, mgr):
        mgr.set("gs", "git status")
        mgr.set("ll", "dir")
        result = mgr.all()
        assert result == {"gs": "git status", "ll": "dir"}


class TestAliasManagerCount:
    def test_count_zero_initially(self, mgr):
        assert mgr.count() == 0

    def test_count_increments_on_set(self, mgr):
        mgr.set("gs", "git status")
        assert mgr.count() == 1

    def test_count_decrements_on_remove(self, mgr):
        mgr.set("gs", "git status")
        mgr.remove("gs")
        assert mgr.count() == 0


class TestAliasManagerClear:
    def test_clear_removes_all(self, mgr):
        mgr.set("gs", "git status")
        mgr.set("ll", "dir")
        mgr.clear()
        assert mgr.count() == 0
        assert mgr.all() == {}
