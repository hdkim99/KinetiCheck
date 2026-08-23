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


@pytest.mark.gui  # type: ignore[untyped-decorator]
@pytest.mark.skipif(  # type: ignore[untyped-decorator]
    not _display_available(), reason="Tk display is unavailable"
)
def test_published_mears_point_through_gui_workflow(tmp_path: Path) -> None:
    """Enter KC-PUB-001 through the real GUI adapter and export its shared-core result."""

    root = tk.Tk()
    root.withdraw()
    try:
        app = KinetiCheckApp(root)
        app.use_wp.set(False)
        app.use_mm.set(True)
        app.use_mh.set(False)
        app.use_ah.set(False)
        values = {
            "run_id": "KC-PUB-001-GUI",
            "rate": "1.014e-4",
            "density": "1099.2",
            "radius": "0.15",
            "order": "6",
            "kc": "0.289",
            "bulk_c": "8.878",
        }
        for key, value in values.items():
            app.values[key].set(value)
        report = app.calculate(show_errors=False)
        assert report is not None
        assert len(report.results) == 1
        assert report.results[0].value == pytest.approx(3.910e-5, rel=2e-4)
        assert len(app.tree.get_children()) == 1
        output = tmp_path / "kc-pub-001-gui.json"
        app.export_to(output)
        assert '"run_id": "KC-PUB-001-GUI"' in output.read_text(encoding="utf-8")
        root.update_idletasks()
    finally:
        root.destroy()
