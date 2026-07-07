"""
test_config.py
Unit tests for rshx.core.config.
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from rshx.core.config import ConfigManager, RshxConfig


@pytest.fixture()
def cfg(tmp_path: Path) -> ConfigManager:
    return ConfigManager(config_file=tmp_path / "config.toml")


class TestRshxConfig:
    def test_default_theme_is_default(self):
        assert RshxConfig().theme == "default"

    def test_default_show_cwd_is_true(self):
        assert RshxConfig().show_cwd is True

    def test_default_show_git_branch_is_false(self):
        assert RshxConfig().show_git_branch is False

    def test_default_aliases_empty(self):
        assert RshxConfig().aliases == {}

    def test_default_environment_empty(self):
        assert RshxConfig().environment == {}

    def test_default_startup_commands_empty(self):
        assert RshxConfig().startup_commands == []


class TestConfigManagerLoad:
    def test_load_creates_default_when_missing(self, cfg, tmp_path):
        cfg.load()
        assert (tmp_path / "config.toml").exists()

    def test_load_recovers_from_corrupted_file(self, cfg, tmp_path):
        (tmp_path / "config.toml").write_text("this is not valid TOML ][[[")
        cfg.load()
        assert cfg.config.theme == "default"

    def test_load_creates_backup_on_corruption(self, cfg, tmp_path):
        (tmp_path / "config.toml").write_text("invalid toml ][")
        cfg.load()
        assert (tmp_path / "config.toml.bak").exists()

    def test_backup_os_error_handled_gracefully(self, cfg, tmp_path):
        """Covers config.py lines 280-281 - OSError during backup rename."""
        (tmp_path / "config.toml").write_text("invalid toml ][")
        with patch("pathlib.Path.rename", side_effect=OSError("rename failed")):
            cfg.load()
        assert cfg.config.theme == "default"

    def test_load_restores_aliases(self, cfg, tmp_path):
        (tmp_path / "config.toml").write_text(
            '[general]\nversion = "0.5.0"\ntheme = "default"\n'
            '[prompt]\nshow_cwd = true\nshow_git_branch = false\n'
            '[aliases]\ngs = "git status"\n'
            '[environment]\n'
            '[startup]\ncommands = []\n'
        )
        cfg.load()
        assert cfg.config.aliases.get("gs") == "git status"

    def test_load_restores_environment(self, cfg, tmp_path):
        (tmp_path / "config.toml").write_text(
            '[general]\nversion = "0.5.0"\ntheme = "default"\n'
            '[prompt]\nshow_cwd = true\nshow_git_branch = false\n'
            '[aliases]\n'
            '[environment]\nEDITOR = "code"\n'
            '[startup]\ncommands = []\n'
        )
        cfg.load()
        assert cfg.config.environment.get("EDITOR") == "code"

    def test_load_restores_startup_commands(self, cfg, tmp_path):
        (tmp_path / "config.toml").write_text(
            '[general]\nversion = "0.5.0"\ntheme = "default"\n'
            '[prompt]\nshow_cwd = true\nshow_git_branch = false\n'
            '[aliases]\n[environment]\n'
            '[startup]\ncommands = ["alias gs=git status"]\n'
        )
        cfg.load()
        assert "alias gs=git status" in cfg.config.startup_commands


class TestConfigManagerSave:
    def test_save_creates_file(self, cfg, tmp_path):
        cfg.save()
        assert (tmp_path / "config.toml").exists()

    def test_save_and_reload_preserves_aliases(self, cfg, tmp_path):
        cfg.load()
        cfg.save_alias("gs", "git status")
        cfg2 = ConfigManager(config_file=tmp_path / "config.toml")
        cfg2.load()
        assert cfg2.config.aliases.get("gs") == "git status"

    def test_save_and_reload_preserves_environment(self, cfg, tmp_path):
        cfg.load()
        cfg.save_variable("EDITOR", "code")
        cfg2 = ConfigManager(config_file=tmp_path / "config.toml")
        cfg2.load()
        assert cfg2.config.environment.get("EDITOR") == "code"

    def test_save_ignores_os_error(self, cfg):
        with patch("pathlib.Path.write_bytes", side_effect=OSError):
            cfg.save()


class TestConfigManagerSetTheme:
    def test_valid_theme_returns_true(self, cfg):
        cfg.load()
        assert cfg.set_theme("dark") is True
        assert cfg.config.theme == "dark"

    def test_invalid_theme_returns_false(self, cfg):
        cfg.load()
        assert cfg.set_theme("rainbow") is False
        assert cfg.config.theme == "default"


class TestConfigManagerSetPromptOptions:
    def test_set_show_cwd_false(self, cfg):
        cfg.load()
        cfg.set_prompt_options(show_cwd=False)
        assert cfg.config.show_cwd is False

    def test_set_show_git_branch_true(self, cfg):
        cfg.load()
        cfg.set_prompt_options(show_git_branch=True)
        assert cfg.config.show_git_branch is True

    def test_partial_update_preserves_other_options(self, cfg):
        cfg.load()
        cfg.set_prompt_options(show_cwd=False)
        assert cfg.config.show_git_branch is False


class TestConfigManagerAliases:
    def test_save_alias(self, cfg):
        cfg.load()
        cfg.save_alias("gs", "git status")
        assert cfg.config.aliases["gs"] == "git status"

    def test_delete_alias(self, cfg):
        cfg.load()
        cfg.save_alias("gs", "git status")
        cfg.delete_alias("gs")
        assert "gs" not in cfg.config.aliases

    def test_delete_nonexistent_alias_does_not_raise(self, cfg):
        cfg.load()
        cfg.delete_alias("nonexistent")


class TestConfigManagerVariables:
    def test_save_variable(self, cfg):
        cfg.load()
        cfg.save_variable("EDITOR", "code")
        assert cfg.config.environment["EDITOR"] == "code"

    def test_delete_variable(self, cfg):
        cfg.load()
        cfg.save_variable("EDITOR", "code")
        cfg.delete_variable("EDITOR")
        assert "EDITOR" not in cfg.config.environment

    def test_delete_nonexistent_variable_does_not_raise(self, cfg):
        cfg.load()
        cfg.delete_variable("nonexistent")


class TestConfigManagerStartupCommands:
    def test_add_startup_command(self, cfg):
        cfg.load()
        cfg.add_startup_command("alias gs=git status")
        assert "alias gs=git status" in cfg.config.startup_commands

    def test_add_duplicate_command_ignored(self, cfg):
        cfg.load()
        cfg.add_startup_command("alias gs=git status")
        cfg.add_startup_command("alias gs=git status")
        assert cfg.config.startup_commands.count("alias gs=git status") == 1

    def test_remove_startup_command(self, cfg):
        cfg.load()
        cfg.add_startup_command("alias gs=git status")
        cfg.remove_startup_command("alias gs=git status")
        assert "alias gs=git status" not in cfg.config.startup_commands

    def test_remove_nonexistent_command_does_not_raise(self, cfg):
        cfg.load()
        cfg.remove_startup_command("nonexistent")


class TestConfigManagerValidate:
    def test_valid_config_returns_empty_list(self, cfg):
        cfg.load()
        assert cfg.validate() == []

    def test_invalid_theme_returns_error_and_resets(self, cfg):
        cfg.load()
        cfg.config.theme = "invalid_theme"
        errors = cfg.validate()
        assert len(errors) > 0
        assert cfg.config.theme == "default"
