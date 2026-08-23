"""Tkinter GUI entry point; imported only when explicitly requested."""

from __future__ import annotations

import platform
import sys
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    try:
        from kineticheck.gui.app import run
    except ImportError as error:
        print(
            "KinetiCheck GUI could not import Tkinter.\n"
            f"Python: {sys.version.split()[0]}\n"
            f"Operating system: {platform.platform()}\n"
            "Install a Python build with Tk support. The scientific core and CLI remain usable.\n"
            "Official command: python -m kineticheck.gui",
            file=sys.stderr,
        )
        print(f"Import detail: {error}", file=sys.stderr)
        return 2
    return run(argv)


__all__ = ["main"]
