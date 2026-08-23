from __future__ import annotations

import os
import tkinter as tk
from pathlib import Path

import pytest

from kineticheck.gui.app import KinetiCheckApp


def _display_available() -> bool:
    return sys_platform_is_macos() or bool(os.environ.get("DISPLAY"))


def sys_platform_is_macos() -> bool:
    import sys

    return sys.platform == "darwin"


@pytest.mark.gui  # type: ignore[untyped-decorator]
@pytest.mark.skipif(  # type: ignore[untyped-decorator]
    not _display_available(), reason="Tk display is unavailable"
)
def test_window_calculation_export_and_close(tmp_path: Path) -> None:
    root = tk.Tk()
    root.withdraw()
    try:
        app = KinetiCheckApp(root)
        report = app.calculate(show_errors=False)
        assert report is not None
        assert len(report.results) == 4
        assert len(app.tree.get_children()) == 4
        output = tmp_path / "gui-result.json"
        app.export_to(output)
        assert '"status": "PASS"' in output.read_text(encoding="utf-8")
        root.update_idletasks()
    finally:
        root.destroy()
