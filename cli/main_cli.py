"""
cli/main_cli.py — backwards-compatibility shim.

main.py now imports `cli` directly from cli.commands.
This module is kept so that `python -m cli.main_cli` still works.
"""

from cli.commands import cli  # noqa: F401

__all__ = ["cli"]

if __name__ == "__main__":
    cli()