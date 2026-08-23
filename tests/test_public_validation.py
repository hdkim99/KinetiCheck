from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import cast

import pytest

from kineticheck.application import evaluate_mapping
from kineticheck.cli import main
from kineticheck.core import mears_external_mass
from kineticheck.models import ScreeningStatus

ROOT = Path(__file__).parents[1]
PUBLIC = ROOT / "examples" / "public_validation"


def _fixture(name: str) -> dict[str, object]:
    payload = json.loads((PUBLIC / name).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("public validation fixture must be an object")
    return cast(dict[str, object], payload)


def test_kc_pub_001_two_methane_dehydroaromatization_points() -> None:
    payload = _fixture("kc-pub-001-mda-mears.json")
    first = evaluate_mapping(payload)
    assert first.results[0].value == pytest.approx(3.910e-5, rel=2e-4)

    second = copy.deepcopy(payload)
    rate = cast(dict[str, object], second["rate"])
    rate["value"] = 2.017e-7
    criteria = cast(dict[str, object], second["criteria"])
    mears = cast(dict[str, object], criteria["mears_mass"])
    concentration = cast(dict[str, object], mears["bulk_concentration"])
    concentration["value"] = 1.081e-2
    replay = evaluate_mapping(second)
    assert replay.results[0].value == pytest.approx(6.387e-5, rel=2e-4)


def test_kc_pub_002_molybdenum_carbide_wp_and_declared_assumption() -> None:
    report = evaluate_mapping(_fixture("kc-pub-002-acetic-acid-wp.json"))
    assert report.results[0].value == pytest.approx(4.96e-6, rel=6e-4)
    assert report.results[0].threshold == 1.0
    assert report.status is ScreeningStatus.WARN
    assert "surface concentration" in report.warnings[0]


@pytest.mark.parametrize(
    ("mass_rate_kmol_kg_s", "density", "radius", "reported"),
    [
        (2.05e-6, 1775.0, 6.617e-6, 7.74e-5),
        (1.54e-6, 1780.0, 6.314e-6, 5.57e-5),
        (7.70e-7, 1788.0, 9.733e-6, 4.31e-5),
    ],
)  # type: ignore[untyped-decorator]
def test_kc_pub_003_three_glycerol_mears_values(
    mass_rate_kmol_kg_s: float,
    density: float,
    radius: float,
    reported: float,
) -> None:
    volumetric_rate = mass_rate_kmol_kg_s * 1000.0 * density
    result = mears_external_mass(volumetric_rate, radius, 1.0, 3.11e-3, 100.0)
    assert result.value == pytest.approx(reported, rel=1.0e-3)


def test_public_fixture_runs_through_cli(tmp_path: Path) -> None:
    output = tmp_path / "kc-pub-003.json"
    assert (
        main(
            [
                "evaluate",
                str(PUBLIC / "kc-pub-003-glycerol-mears.json"),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["run_id"] == "KC-PUB-003-PT1-PTN-GLYCEROL"
    assert report["results"][0]["value"] == pytest.approx(7.74e-5, rel=1.0e-3)


def test_source_and_failure_registers_are_structured_and_complete() -> None:
    sources = json.loads((ROOT / "docs" / "public-data-sources.json").read_text(encoding="utf-8"))
    failures = json.loads(
        (ROOT / "docs" / "public-validation-failures.json").read_text(encoding="utf-8")
    )
    records = sources["sources"]
    assert [record["id"] for record in records] == [
        "KC-PUB-001",
        "KC-PUB-002",
        "KC-PUB-003",
        "KC-PUB-004",
        "KC-PUB-005",
        "KC-PUB-006",
    ]
    accepted = records[:3]
    assert all(record["source_file"]["sha256"] for record in accepted)
    assert all(record["source_file"]["redistributed"] is False for record in records)
    assert failures["software_defects_found"] == 0
    assert "SOFTWARE_DEFECT" in failures["taxonomy"]
    assert all(item["category"] != "SOFTWARE_DEFECT" for item in failures["findings"])
