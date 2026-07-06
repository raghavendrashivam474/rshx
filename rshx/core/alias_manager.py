"""
alias_manager.py
----------------
Manages user-defined aliases for the current shell session.

An alias maps a short name to a full command string.
When the preprocessor encounters a command whose first token
matches a registered alias, it replaces that token with the
alias value before passing the command to the parser.

Aliases are session-scoped. Persistence is out of scope for
Sprint 3 and will be introduced in Sprint 4.

Responsibilities
----------------
- Store aliases in an internal dictionary.
- Create, overwrite, delete, and look up aliases.
- List all currently registered aliases.
- Validate alias names and values.
"""

from __future__ import annotations


class AliasManager:
    """
    Manages the alias registry for an RSHX session.

    Attributes
    ----------
    _aliases : dict[str, str]
        Maps alias name to its expansion string.
    """

    def __init__(self) -> None:
        self._aliases: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def set(self, name: str, value: str) -> None:
        """
        Create or overwrite an alias.

        Parameters
        ----------
        name : str
            The alias name. Must be a non-empty string containing
            no whitespace.
        value : str
            The command string the alias expands to. Must be
            non-empty.

        Raises
        ------
        ValueError
            When name or value is empty or name contains whitespace.
        """
        if not name or not name.strip():
            raise ValueError("Alias name cannot be empty.")

        if " " in name or "\t" in name:
            raise ValueError(
                f"Alias name '{name}' must not contain whitespace."
            )

        if not value or not value.strip():
            raise ValueError("Alias value cannot be empty.")

        self._aliases[name] = value

    def remove(self, name: str) -> None:
        """
        Remove an alias by name.

        Parameters
        ----------
        name : str
            The alias name to remove.

        Raises
        ------
        KeyError
            When the alias does not exist.
        """
        if name not in self._aliases:
            raise KeyError(f"Alias '{name}' not found.")

        del self._aliases[name]

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, name: str) -> str | None:
        """
        Look up an alias by name.

        Parameters
        ----------
        name : str
            The alias name to look up.

        Returns
        -------
        str | None
            The expansion string, or None if the alias does not exist.
        """
        return self._aliases.get(name)

    def exists(self, name: str) -> bool:
        """Return True when the alias name is registered."""
        return name in self._aliases

    def all(self) -> dict[str, str]:
        """
        Return a copy of all registered aliases.

        Returns a copy so callers cannot mutate internal state.

        Returns
        -------
        dict[str, str]
            Mapping of alias name to expansion string.
        """
        return dict(self._aliases)

    def count(self) -> int:
        """Return the number of registered aliases."""
        return len(self._aliases)

    def clear(self) -> None:
        """Remove all aliases."""
        self._aliases.clear()
