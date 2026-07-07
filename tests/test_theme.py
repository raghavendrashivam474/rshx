"""
test_theme.py
Unit tests for rshx.core.theme.
"""

from rshx.core.theme import get_theme, list_themes, is_valid_theme, THEMES, DEFAULT_THEME_NAME


class TestGetTheme:
    def test_returns_default_theme(self):
        theme = get_theme("default")
        assert theme.name == "default"

    def test_returns_dark_theme(self):
        theme = get_theme("dark")
        assert theme.name == "dark"

    def test_returns_light_theme(self):
        theme = get_theme("light")
        assert theme.name == "light"

    def test_unknown_name_returns_default(self):
        theme = get_theme("nonexistent")
        assert theme.name == DEFAULT_THEME_NAME

    def test_all_themes_have_required_fields(self):
        required = [
            "name", "prompt_shell", "prompt_cwd", "prompt_arrow",
            "success", "error", "warning", "info", "output", "banner",
        ]
        for theme in THEMES.values():
            for field in required:
                assert hasattr(theme, field)


class TestListThemes:
    def test_returns_list(self):
        result = list_themes()
        assert isinstance(result, list)

    def test_contains_default(self):
        assert "default" in list_themes()

    def test_contains_dark(self):
        assert "dark" in list_themes()

    def test_contains_light(self):
        assert "light" in list_themes()

    def test_is_sorted(self):
        result = list_themes()
        assert result == sorted(result)


class TestIsValidTheme:
    def test_default_is_valid(self):
        assert is_valid_theme("default") is True

    def test_dark_is_valid(self):
        assert is_valid_theme("dark") is True

    def test_light_is_valid(self):
        assert is_valid_theme("light") is True

    def test_unknown_is_invalid(self):
        assert is_valid_theme("rainbow") is False

    def test_empty_string_is_invalid(self):
        assert is_valid_theme("") is False
