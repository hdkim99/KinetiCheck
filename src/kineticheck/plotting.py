"""Deferred matplotlib plotting; importing this module does not import pyplot."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, cast

from kineticheck.models import ScreeningReport


def plot_envelope(
    reports: list[ScreeningReport],
    criterion_symbol: str,
    output: Path,
    *,
    backend: str = "Agg",
) -> None:
    """Plot a batch sequence against the declared criterion threshold."""

    if output.suffix.lower() not in {".png", ".svg", ".pdf"}:
        raise ValueError("plot output must be PNG, SVG, or PDF")
    matplotlib = importlib.import_module("matplotlib")
    matplotlib.use(backend, force=True)
    plt = cast(Any, importlib.import_module("matplotlib.pyplot"))

    points: list[tuple[str, float, float, str]] = []
    for report in reports:
        for result in report.results:
            if result.symbol.casefold() == criterion_symbol.casefold():
                points.append((report.run_id, result.value, result.threshold, result.status.value))
                break
    if not points:
        raise ValueError(f"criterion {criterion_symbol!r} is absent from all reports")
    x = list(range(len(points)))
    values = [point[1] for point in points]
    thresholds = [point[2] for point in points]
    colors = ["#b42318" if point[3] == "FAIL" else "#147d64" for point in points]
    figure, axis = plt.subplots(figsize=(8.0, 4.0), constrained_layout=True)
    axis.plot(x, values, color="#244766", linewidth=1.5, zorder=1)
    axis.scatter(x, values, c=colors, s=48, zorder=2, label="operating points")
    axis.plot(x, thresholds, color="#d48a00", linestyle="--", label="declared threshold")
    axis.fill_between(x, thresholds, color="#f4c95d", alpha=0.12)
    axis.set_xticks(x, [point[0] for point in points], rotation=30, ha="right")
    axis.set_ylabel(f"{criterion_symbol} (dimensionless)")
    axis.set_xlabel("Operating point")
    axis.set_title("KinetiCheck transport-screening envelope")
    axis.grid(axis="y", alpha=0.25)
    axis.legend()
    figure.savefig(output, dpi=160)
    plt.close(figure)
