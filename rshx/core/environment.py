"""
environment.py
--------------
Manages user-defined environment variables for the shell session.

Variables are referenced using %VARNAME% syntax, consistent with
Windows CMD convention. The variable resolver replaces all
occurrences of %VARNAME% in the input string with the stored value
before the command is passed to the parser.

Variables are session-scoped. Persistence is out of scope for
Sprint 3 and will be introduced in Sprint 4.

Responsibilities
----------------
- Store variables in an internal dictionary.
- Create, overwrite, delete, and look up variables.
- Expand %VARNAME% references in command strings.
- Handle undefined variable references gracefully.
"""

from __future__ import annotations
import re


# Pattern matches %VARNAME% references in command strings
_VAR_PATTERN = re.compile(r"%([A-Za-z_][A-Za-z0-9_]*)%")


class Environment:
    """
    Manages the environment variable registry for an RSHX session.

    Attributes
    ----------
    _variables : dict[str, str]
        Maps variable name to its string value.
    """

    def __init__(self) -> None:
        self._variables: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

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
        """
        Remove a variable by name.

        Parameters
        ----------
        name : str
            The variable name to remove.

        Raises
        ------
        KeyError
            When the variable does not exist.
        """
        if name not in self._variables:
            raise KeyError(f"Variable '{name}' not found.")

        del self._variables[name]

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, name: str) -> str | None:
        """
        Look up a variable by name.

        Parameters
        ----------
        name : str
            The variable name to look up.

        Returns
        -------
        str | None
            The variable value, or None if not defined.
        """
        return self._variables.get(name)

    def exists(self, name: str) -> bool:
        """Return True when the variable name is defined."""
        return name in self._variables

    def all(self) -> dict[str, str]:
        """
        Return a copy of all defined variables.

        Returns
        -------
        dict[str, str]
            Mapping of variable name to value.
        """
        return dict(self._variables)

    def count(self) -> int:
        """Return the number of defined variables."""
        return len(self._variables)

    def clear(self) -> None:
        """Remove all variables."""
        self._variables.clear()

    # ------------------------------------------------------------------
    # Expansion
    # ------------------------------------------------------------------

    def expand(self, text: str) -> tuple[str, list[str]]:
        """
        Expand all %VARNAME% references in the given text.

        Replaces each %VARNAME% occurrence with the stored value.
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
            A tuple of (expanded_text, warnings) where warnings is
            a list of messages about undefined variable references.
        """
        warnings: list[str] = []

        def replace(match: re.Match) -> str:
            var_name = match.group(1)
            value = self._variables.get(var_name)

            if value is None:
                warnings.append(
                    f"Warning: variable '%{var_name}%' is not defined."
                )
                return match.group(0)

            return value

        expanded = _VAR_PATTERN.sub(replace, text)
        return expanded, warnings
