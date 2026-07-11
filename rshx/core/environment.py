"""
environment.py
--------------
Manages user-defined environment variables for the shell session.

Variables are referenced using %VARNAME% syntax.
Positional script arguments are available as %1 %2 %3 etc.
"""

from __future__ import annotations
import re


# Pattern matches %VARNAME% - allows letters, digits, underscores
# Also allows pure digit names for positional args %1 %2 %3
_VAR_PATTERN = re.compile(r"%([A-Za-z_][A-Za-z0-9_]*|[0-9]+)%")


class Environment:
    """
    Manages the environment variable registry for an RSHX session.
    """

    def __init__(self) -> None:
        self._variables: dict[str, str] = {}

    def set(self, name: str, value: str) -> None:
        """
        Create or overwrite an environment variable.

        Parameters
        ----------
        name : str
            Variable name. Must be non-empty and contain only
            alphanumeric characters and underscores.
        value : str
            Variable value. May be any string including empty.

        Raises
        ------
        ValueError
            When the name is empty or contains invalid characters.
        """
        if not name or not name.strip():
            raise ValueError("Variable name cannot be empty.")

        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            raise ValueError(
                f"Variable name '{name}' contains invalid characters. "
                "Names must start with a letter or underscore and "
                "contain only letters, digits, and underscores."
            )

        self._variables[name] = value

    def remove(self, name: str) -> None:
        """Remove a variable by name."""
        if name not in self._variables:
            raise KeyError(f"Variable '{name}' not found.")
        del self._variables[name]

    def get(self, name: str) -> str | None:
        """Look up a variable by name."""
        return self._variables.get(name)

    def exists(self, name: str) -> bool:
        """Return True when the variable name is defined."""
        return name in self._variables

    def all(self) -> dict[str, str]:
        """Return a copy of all defined variables."""
        return dict(self._variables)

    def count(self) -> int:
        """Return the number of defined variables."""
        return len(self._variables)

    def clear(self) -> None:
        """Remove all variables."""
        self._variables.clear()

    def expand(self, text: str) -> tuple[str, list[str]]:
        """
        Expand all %VARNAME% and %1 %2 %3 references in the given text.

        Replaces each %VARNAME% or %N% occurrence with the stored value.
        Undefined variable references are left unchanged and
        reported in the warnings list.

        Parameters
        ----------
        text : str
            The raw command string containing zero or more variable
            references.

        Returns
        -------
        tuple[str, list[str]]
            A tuple of (expanded_text, warnings).
        """
        warnings: list[str] = []

        def replace(match: re.Match) -> str:
            var_name = match.group(1)
            value = self._variables.get(var_name)

            if value is None:
                warnings.append(
                    f"variable '%{var_name}%' is not defined."
                )
                return match.group(0)

            return value

        expanded = _VAR_PATTERN.sub(replace, text)
        return expanded, warnings
