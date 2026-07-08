"""
test_plugin_loader.py
Unit tests for rshx.core.plugin_loader.
"""

from pathlib import Path
import pytest

from rshx.core.plugin_loader import (
    discover_plugins,
    load_manifest,
    load_plugin_module,
    validate_plugin_module,
    load_plugin,
    PluginManifest,
    LoadedPlugin,
)


def make_plugin(tmp_path: Path, name: str, manifest: str, code: str) -> Path:
    plugin_dir = tmp_path / name
    plugin_dir.mkdir()
    (plugin_dir / "manifest.toml").write_text(manifest, encoding="utf-8")
    (plugin_dir / "plugin.py").write_text(code, encoding="utf-8")
    return plugin_dir


VALID_MANIFEST = '''
name = "test"
version = "1.0.0"
description = "A test plugin"
author = "Tester"
commands = ["test_cmd"]
'''

VALID_CODE = '''
def initialise(api):
    pass

def shutdown():
    pass
'''


class TestDiscoverPlugins:
    def test_discovers_valid_plugin(self, tmp_path):
        make_plugin(tmp_path, "myplugin", VALID_MANIFEST, VALID_CODE)
        result = discover_plugins(tmp_path)
        assert len(result) == 1
        assert result[0].name == "myplugin"

    def test_ignores_directories_without_manifest(self, tmp_path):
        d = tmp_path / "nomanifest"
        d.mkdir()
        (d / "plugin.py").write_text("", encoding="utf-8")
        result = discover_plugins(tmp_path)
        assert result == []

    def test_ignores_directories_without_plugin_py(self, tmp_path):
        d = tmp_path / "nopluginpy"
        d.mkdir()
        (d / "manifest.toml").write_text(VALID_MANIFEST, encoding="utf-8")
        result = discover_plugins(tmp_path)
        assert result == []

    def test_ignores_underscore_directories(self, tmp_path):
        make_plugin(tmp_path, "__pycache__", VALID_MANIFEST, VALID_CODE)
        result = discover_plugins(tmp_path)
        assert result == []

    def test_returns_empty_when_directory_missing(self, tmp_path):
        result = discover_plugins(tmp_path / "nonexistent")
        assert result == []

    def test_returns_sorted_list(self, tmp_path):
        make_plugin(tmp_path, "zzz", VALID_MANIFEST, VALID_CODE)
        make_plugin(tmp_path, "aaa", VALID_MANIFEST, VALID_CODE)
        result = discover_plugins(tmp_path)
        names = [p.name for p in result]
        assert names == sorted(names)


class TestLoadManifest:
    def test_loads_valid_manifest(self, tmp_path):
        plugin_dir = make_plugin(tmp_path, "p", VALID_MANIFEST, VALID_CODE)
        manifest = load_manifest(plugin_dir)
        assert manifest is not None
        assert manifest.name == "test"
        assert manifest.version == "1.0.0"

    def test_returns_none_for_missing_fields(self, tmp_path):
        plugin_dir = tmp_path / "bad"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.toml").write_text(
            'name = "only_name"\n', encoding="utf-8"
        )
        assert load_manifest(plugin_dir) is None

    def test_returns_none_for_invalid_toml(self, tmp_path):
        plugin_dir = tmp_path / "bad"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.toml").write_text("][broken", encoding="utf-8")
        assert load_manifest(plugin_dir) is None

    def test_commands_defaults_to_empty_list(self, tmp_path):
        manifest_no_cmds = '''
name = "test"
version = "1.0.0"
description = "desc"
author = "auth"
commands = []
'''
        plugin_dir = make_plugin(tmp_path, "p", manifest_no_cmds, VALID_CODE)
        manifest = load_manifest(plugin_dir)
        assert manifest.commands == []


class TestLoadPluginModule:
    def test_loads_valid_module(self, tmp_path):
        plugin_dir = make_plugin(tmp_path, "p", VALID_MANIFEST, VALID_CODE)
        module = load_plugin_module(plugin_dir)
        assert module is not None
        assert hasattr(module, "initialise")

    def test_returns_none_for_syntax_error(self, tmp_path):
        plugin_dir = make_plugin(tmp_path, "p", VALID_MANIFEST, "def broken(: pass")
        module = load_plugin_module(plugin_dir)
        assert module is None


class TestValidatePluginModule:
    def test_valid_module_returns_true(self, tmp_path):
        plugin_dir = make_plugin(tmp_path, "p", VALID_MANIFEST, VALID_CODE)
        module = load_plugin_module(plugin_dir)
        assert validate_plugin_module(module) is True

    def test_module_without_initialise_returns_false(self, tmp_path):
        plugin_dir = make_plugin(tmp_path, "p", VALID_MANIFEST, "x = 1")
        module = load_plugin_module(plugin_dir)
        assert validate_plugin_module(module) is False


class TestLoadPlugin:
    def test_loads_valid_plugin(self, tmp_path):
        plugin_dir = make_plugin(tmp_path, "p", VALID_MANIFEST, VALID_CODE)
        result = load_plugin(plugin_dir)
        assert isinstance(result, LoadedPlugin)
        assert result.manifest.name == "test"
        assert result.enabled is True

    def test_returns_none_for_invalid_manifest(self, tmp_path):
        plugin_dir = tmp_path / "bad"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.toml").write_text("][broken", encoding="utf-8")
        (plugin_dir / "plugin.py").write_text(VALID_CODE, encoding="utf-8")
        assert load_plugin(plugin_dir) is None

    def test_returns_none_for_invalid_module(self, tmp_path):
        plugin_dir = make_plugin(tmp_path, "p", VALID_MANIFEST, "x =")
        assert load_plugin(plugin_dir) is None
