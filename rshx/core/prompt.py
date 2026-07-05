"""
prompt.py
---------
Builds the dynamic prompt displayed to the user.

Keeping prompt rendering in its own module means the visual
format can be changed in one place without touching the REPL.

Prompt format
-------------
RSHX
<cwd> >

Example
-------
RSHX
C:/Projects/rshx >
"""

from pathlib import Path
from prompt_toolkit.formatted_text import HTML


def build_prompt(cwd: Path) -> HTML:
    """
    Build the RSHX prompt as a prompt_toolkit HTML object.

    Displays the shell name on one line and the current working
    directory followed by the > character on the next.

    Parameters
    ----------
    cwd : Path
        The shell's current working directory.

    Returns
    -------
    HTML
        A formatted prompt object consumed by PromptSession.
    """
    cwd_str: str = str(cwd)

    return HTML(
        f"<ansigreen><b>RSHX</b></ansigreen>\n"
        f"<ansicyan>{cwd_str}</ansicyan>"
        f"<ansiwhite> &gt; </ansiwhite>"
    )
