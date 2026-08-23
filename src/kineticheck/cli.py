"""Headless command-line adapter."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from kineticheck import __version__
from kineticheck.application import evaluate_mapping
from kineticheck.io import read_batch, write_reports


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kineticheck",
        description="Screen stated catalytic operating points for selected transport limitations.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    evaluate = commands.add_parser("evaluate", help="Evaluate one JSON operating point")
    evaluate.add_argument("input", type=Path)
    evaluate.add_argument("--output", type=Path)
    batch = commands.add_parser("batch", help="Evaluate CSV or XLSX operating points")
    batch.add_argument("input", type=Path)
    batch.add_argument("--output", type=Path, required=True)
    plot = commands.add_parser("plot", help="Plot a criterion from a batch input")
    plot.add_argument("input", type=Path)
    plot.add_argument("--criterion", default="C_WP", choices=("C_WP", "C_MM", "C_MH", "C_AH"))
    plot.add_argument("--output", type=Path, required=True)
    commands.add_parser("validate", help="Run the documented hand-calculated benchmark")
    return parser


def _load_json(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("operating-point JSON must contain an object")
    return cast(dict[str, object], loaded)


def _validated_demo() -> dict[str, object]:
    return {
        "run_id": "hand-check",
        "rate": {"value": 2.0, "unit": "mol / meter ** 3 / second", "basis": "pellet_volume"},
        "particle_radius": {"value": 1.0, "unit": "millimeter"},
        "criteria": {
            "weisz_prater": {
                "effective_diffusivity": {"value": 1.0e-5, "unit": "meter ** 2 / second"},
                "surface_concentration": {"value": 10.0, "unit": "mol / meter ** 3"},
            },
            "mears_mass": {
                "reaction_order": 1.0,
                "mass_transfer_coefficient": {"value": 0.02, "unit": "meter / second"},
                "bulk_concentration": {"value": 10.0, "unit": "mol / meter ** 3"},
            },
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "evaluate":
            report = evaluate_mapping(_load_json(args.input))
            text = json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n"
            if args.output is None:
                sys.stdout.write(text)
            else:
                args.output.write_text(text, encoding="utf-8")
            return 0
        if args.command == "batch":
            reports = read_batch(args.input)
            write_reports(reports, args.output)
            print(f"Evaluated {len(reports)} operating points -> {args.output}")
            return 0
        if args.command == "plot":
            from kineticheck.plotting import plot_envelope

            reports = read_batch(args.input)
            plot_envelope(reports, args.criterion, args.output, backend="Agg")
            print(f"Wrote {args.criterion} envelope -> {args.output}")
            return 0
        report = evaluate_mapping(_validated_demo())
        observed = {item.symbol: item.value for item in report.results}
        expected = {"C_WP": 0.02, "C_MM": 0.01}
        for key, value in expected.items():
            if abs(observed[key] - value) > 1e-12:
                raise RuntimeError(f"benchmark mismatch for {key}: {observed[key]} != {value}")
        print("Hand benchmark PASS: C_WP=0.02, C_MM=0.01")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"kineticheck: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
