from __future__ import annotations

import copy

import pytest

from kineticheck.application import evaluate_mapping
from kineticheck.models import ScreeningStatus
from kineticheck.units import RateBasis, normalize_rate


@pytest.fixture  # type: ignore[untyped-decorator]
def point() -> dict[str, object]:
    return {
        "run_id": "u-1",
        "rate": {
            "value": 7.2,
            "unit": "mol / gram / hour",
            "basis": "mass_catalyst",
            "pellet_density": {"value": 1.0, "unit": "gram / centimeter ** 3"},
        },
        "particle_radius": {"value": 1000.0, "unit": "micrometer"},
        "criteria": {
            "weisz_prater": {
                "effective_diffusivity": {"value": 0.1, "unit": "centimeter ** 2 / second"},
                "surface_concentration": {"value": 0.01, "unit": "mol / liter"},
            }
        },
    }


def test_mass_rate_and_mixed_units_are_explicit(point: dict[str, object]) -> None:
    report = evaluate_mapping(point)
    assert report.volumetric_rate_mol_m3_s == pytest.approx(2000.0)
    assert report.results[0].value == pytest.approx(20.0)
    assert report.status is ScreeningStatus.FAIL
    assert "apparent pellet density" in report.rate_conversion


def test_bed_basis_requires_void_fraction() -> None:
    with pytest.raises(ValueError, match="bed_void_fraction"):
        normalize_rate(1.0, "mol/m^3/s", RateBasis.BED_VOLUME)
    converted = normalize_rate(
        0.6,
        "mol/m^3/s",
        RateBasis.BED_VOLUME,
        bed_void_fraction=0.4,
    )
    assert converted.value_mol_m3_s == pytest.approx(1.0)


def test_mass_basis_requires_density(point: dict[str, object]) -> None:
    altered = copy.deepcopy(point)
    rate = altered["rate"]
    assert isinstance(rate, dict)
    del rate["pellet_density"]
    with pytest.raises(ValueError, match="pellet_density"):
        evaluate_mapping(altered)


def test_surface_equals_bulk_declaration_produces_warning(point: dict[str, object]) -> None:
    criteria = point["criteria"]
    assert isinstance(criteria, dict)
    wp = criteria["weisz_prater"]
    assert isinstance(wp, dict)
    wp["surface_concentration_assumed_bulk"] = True
    rate = point["rate"]
    assert isinstance(rate, dict)
    rate["value"] = 0.0072
    report = evaluate_mapping(point)
    assert report.warnings
    assert report.status is ScreeningStatus.WARN


def test_incompatible_unit_is_rejected(point: dict[str, object]) -> None:
    radius = point["particle_radius"]
    assert isinstance(radius, dict)
    radius["unit"] = "kelvin"
    with pytest.raises(ValueError, match="particle_radius"):
        evaluate_mapping(point)
