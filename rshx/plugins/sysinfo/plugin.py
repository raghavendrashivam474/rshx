"""
sysinfo plugin
--------------
Provides system information commands.

Registers two commands:
- sysinfo : display OS and Python information
- uptime  : display system uptime
"""

from __future__ import annotations
import platform
import sys
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rshx.core.plugin_api import PluginAPI
    from rshx.core.repl import ShellState

_api = None


def initialise(api: "PluginAPI") -> None:
    """Register plugin commands with the shell."""
    global _api
    _api = api

    api.register_command(
        name="sysinfo",
        handler=_cmd_sysinfo,
        description="Display operating system and Python information.",
    )

    api.register_command(
        name="uptime",
        handler=_cmd_uptime,
        description="Display system uptime.",
    )

    api.register_help(
        command="sysinfo",
        description="Display operating system and Python information.",
        usage="sysinfo",
        examples="sysinfo",
        notes="Shows OS, architecture, Python version, and hostname.",
    )

    api.register_help(
        command="uptime",
        description="Display system uptime.",
        usage="uptime",
        examples="uptime",
        notes="Uses platform-appropriate system calls.",
    )


def shutdown() -> None:
    pass


def _cmd_sysinfo(args: list[str], shell_state: "ShellState") -> None:
    _api.print_output("")
    _api.print_output("  System Information")
    _api.print_output("  " + "-" * 40)
    _api.print_output(f"  OS          : {platform.system()} {platform.release()}")
    _api.print_output(f"  Version     : {platform.version()[:50]}")
    _api.print_output(f"  Architecture: {platform.machine()}")
    _api.print_output(f"  Hostname    : {platform.node()}")
    _api.print_output(f"  Python      : {sys.version.split()[0]}")
    _api.print_output(f"  Processor   : {platform.processor() or 'unknown'}")
    _api.print_output("")


def _cmd_uptime(args: list[str], shell_state: "ShellState") -> None:
    try:
        if platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                ["net", "statistics", "workstation"],
                capture_output=True,
                text=True,
                shell=True,
            )
            lines = result.stdout.splitlines()
            for line in lines:
                if "Statistics since" in line:
                    _api.print_output(f"  {line.strip()}")
                    return
            _api.print_output("  Uptime information not available.")
        else:
            import subprocess
            result = subprocess.run(
                ["uptime"],
                capture_output=True,
                text=True,
            )
            _api.print_output(f"  {result.stdout.strip()}")
    except Exception as exc:
        _api.print_error(f"uptime: {exc}")
