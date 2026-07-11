"""
test_script_loader.py
Unit tests for rshx.core.script_loader.
"""

import os
from pathlib import Path
import pytest
from rshx.core.script_loader import load_script, SCRIPT_EXTENSION


@pytest.fixture()
def script_dir(tmp_path: Path) -> Path:
    return tmp_path


def make_script(directory: Path, name: str, content: str = "pwd") -> Path:
    path = directory / name
    path.write_text(content, encoding="utf-8")
    return path


class TestLoadScriptSuccess:
    def test_loads_valid_script(self, script_dir):
        make_script(script_dir, "test.rshx", "pwd\ngit status\n")
        loaded, error = load_script("test.rshx", cwd=script_dir)
        assert loaded is not None
        assert error == ""
        assert "pwd" in loaded.source

    def test_returns_absolute_path(self, script_dir):
        make_script(script_dir, "test.rshx")
        loaded, _ = load_script("test.rshx", cwd=script_dir)
        assert loaded.path.is_absolute()

    def test_loads_empty_script(self, script_dir):
        make_script(script_dir, "empty.rshx", "")
        loaded, error = load_script("empty.rshx", cwd=script_dir)
        assert loaded is not None
        assert loaded.source == ""

    def test_loads_utf8_content(self, script_dir):
        content = "# Unicode: \u00e9\u00e0\u00fc\npwd\n"
        make_script(script_dir, "unicode.rshx", content)
        loaded, error = load_script("unicode.rshx", cwd=script_dir)
        assert loaded is not None
        assert "\u00e9" in loaded.source

    def test_relative_path_resolved_against_cwd(self, script_dir):
        sub = script_dir / "sub"
        sub.mkdir()
        make_script(sub, "test.rshx")
        loaded, error = load_script("sub/test.rshx", cwd=script_dir)
        assert loaded is not None

    def test_absolute_path_works(self, script_dir):
        path = make_script(script_dir, "test.rshx")
        loaded, error = load_script(str(path), cwd=script_dir)
        assert loaded is not None


class TestLoadScriptFailures:
    def test_missing_file_returns_error(self, script_dir):
        loaded, error = load_script("nonexistent.rshx", cwd=script_dir)
        assert loaded is None
        assert "not found" in error.lower() or "nonexistent" in error

    def test_directory_path_returns_error(self, script_dir):
        sub = script_dir / "mydir.rshx"
        sub.mkdir()
        loaded, error = load_script("mydir.rshx", cwd=script_dir)
        assert loaded is None
        assert "not a file" in error.lower()

    def test_invalid_extension_returns_error(self, script_dir):
        path = script_dir / "test.txt"
        path.write_text("pwd", encoding="utf-8")
        loaded, error = load_script("test.txt", cwd=script_dir)
        assert loaded is None
        assert ".rshx" in error or "extension" in error.lower()

    def test_uppercase_extension_on_case_insensitive_fs(self, script_dir):
        """
        On Windows (case-insensitive filesystem) .RSHX == .rshx
        so the file loads successfully. On Linux it would fail.
        This test documents the platform-specific behaviour.
        """
        path = script_dir / "test.RSHX"
        path.write_text("pwd", encoding="utf-8")
        loaded, error = load_script("test.RSHX", cwd=script_dir)

        if os.name == "nt":
            # Windows: case-insensitive - .RSHX resolves to .rshx
            assert loaded is not None
        else:
            # Unix: case-sensitive - .RSHX != .rshx
            assert loaded is None

    def test_non_utf8_file_returns_error(self, script_dir):
        path = script_dir / "bad.rshx"
        path.write_bytes(b"\xff\xfe invalid utf-8 \x00\x01")
        loaded, error = load_script("bad.rshx", cwd=script_dir)
        assert loaded is None
        assert "UTF-8" in error or "utf" in error.lower()
