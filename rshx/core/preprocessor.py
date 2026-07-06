"""
preprocessor.py
---------------
Transforms raw user input before it reaches the parser.

Processing order
----------------
1. Alias expansion   - replace leading alias names with their values
2. Variable expansion - replace %VARNAME% references with stored values

The preprocessor owns no state of its own. It receives
AliasManager and Environment instances and coordinates
their operations.

The parser receives only the fully expanded command string.
The parser never knows that aliases or variables existed.

Responsibilities
----------------
- Coordinate alias resolution.
- Coordinate variable expansion.
- Return the transformed command string and any warnings.
- Perform no parsing.
- Perform no execution.
"""

from __future__ import annotations
from rshx.core.alias_manager import AliasManager
from rshx.core.environment import Environment


class Preprocessor:
    """
    Transforms raw input into a fully expanded command string.

    Parameters
    ----------
    alias_manager : AliasManager
        The session alias registry.
    environment : Environment
        The session environment variable registry.
    """

    def __init__(
        self,
        alias_manager: AliasManager,
        environment: Environment,
    ) -> None:
        self._aliases = alias_manager
        self._env = environment

    def process(self, raw_input: str) -> tuple[str, list[str]]:
        """
        Apply alias expansion and variable expansion to raw input.

        Processing order
        ----------------
        1. Strip leading and trailing whitespace.
        2. Attempt alias expansion on the first token.
        3. Apply variable expansion to the entire resulting string.

        Parameters
        ----------
        raw_input : str
            The raw command string entered by the user.

        Returns
        -------
        tuple[str, list[str]]
            A tuple of (expanded_command, warnings) where warnings
            is a list of informational or warning messages produced
            during expansion.
        """
        warnings: list[str] = []
        text = raw_input.strip()

        if not text:
            return text, warnings

        # Step 1 - Alias expansion
        text = self._expand_alias(text)

        # Step 2 - Variable expansion
        text, var_warnings = self._env.expand(text)
        warnings.extend(var_warnings)

        return text, warnings

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _expand_alias(self, text: str) -> str:
        """
        Expand the first token of the command if it is a known alias.

        Only the first token is checked for alias expansion to match
        standard shell behaviour. Arguments following the alias name
        are preserved unchanged.

        Parameters
        ----------
        text : str
            The command string after whitespace stripping.

        Returns
        -------
        str
            The command string with the leading alias expanded, or
            the original string if no alias matched.
        """
        parts = text.split(None, 1)
        first_token = parts[0]

        expansion = self._aliases.get(first_token)

        if expansion is None:
            return text

        # Replace the alias name with its expansion
        # Preserve any arguments that followed the alias
        if len(parts) > 1:
            return f"{expansion} {parts[1]}"

        return expansion
