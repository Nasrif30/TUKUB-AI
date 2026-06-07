#!/usr/bin/env python3
"""
TUKUB AI - Autonomous Security Agent
From Tausug language: "tukub" - to fight/attack like animals over territory
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Fix Windows console encoding for Unicode art
if sys.platform == "win32":
    try:
        # sys.stdout is TextIOWrapper at runtime (supports reconfigure),
        # but typed as TextIO — use hasattr to satisfy both type checkers.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

from rich.console import Console

console = Console()

ASCII_BANNER = """
    ████████╗██╗   ██╗██╗  ██╗██╗   ██╗██████╗     █████╗ ██╗
    ╚══██╔══╝██║   ██║██║ ██╔╝██║   ██║██╔══██╗   ██╔══██╗██║
       ██║   ██║   ██║█████╔╝ ██║   ██║██████╔╝   ███████║██║
       ██║   ██║   ██║██╔═██╗ ██║   ██║██╔══██╗   ██╔══██║██║
       ██║   ╚██████╔╝██║  ██╗╚██████╔╝██████╔╝   ██║  ██║██║
       ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝    ╚═╝  ╚═╝╚═╝
"""


def show_banner():
    console.print(ASCII_BANNER, style="cyan")
    console.print("=" * 70, style="white")
    console.print(
        "tukub (tə-ˈküb) - Tausug (Philippines) verb: to fight, to attack\n"
        '"Like beasts fighting over territory, we hunt vulnerabilities"',
        justify="center",
        style="yellow",
    )
    console.print(
        "AUTHORIZED USE ONLY - Unauthorized access is illegal",
        justify="center",
        style="red",
    )
    console.print(
        "Author: A. HALIDDIN | GitHub: https://github.com/Nasrif30",
        justify="center",
        style="dim cyan",
    )
    console.print("=" * 70, style="white")
    console.print()


def main():
    show_banner()
    from cli.commands import cli
    cli(standalone_mode=True)


if __name__ == "__main__":
    main()