from __future__ import annotations

import math

import pytest

from kineticheck.core import (
    anderson_internal_heat,
    mears_external_heat,
    mears_external_mass,
    weisz_prater,
)
from kineticheck.models import ScreeningStatus


def test_hand_calculated_four_criteria() -> None:
    rate = 2.0
    radius = 1.0e-3
    wp = weisz_prater(rate, radius, 1.0e-5, 10.0)
    mm = mears_external_mass(rate, radius, 1.0, 0.02, 10.0)
    mh = mears_external_heat(rate, radius, -100_000.0, 80_000.0, 250.0, 600.0)
    ah = anderson_internal_heat(rate, radius, -100_000.0, 80_000.0, 0.5, 600.0)
    assert wp.value == pytest.approx(0.02)
    assert mm.value == pytest.approx(0.01)
    assert mh.value == pytest.approx(0.021381752007595737)
    assert ah.value == pytest.approx(0.010690876003797868)
    assert {wp.status, mm.status, mh.status, ah.status} == {ScreeningStatus.PASS}


def test_threshold_is_strict_and_override_is_recorded() -> None:
    result = weisz_prater(30.0, 1.0e-3, 1.0e-5, 10.0)
    assert result.value == pytest.approx(0.3)
    assert result.status is ScreeningStatus.FAIL
    override = weisz_prater(30.0, 1.0e-3, 1.0e-5, 10.0, threshold=0.31)
    assert override.status is ScreeningStatus.PASS
    assert override.threshold == 0.31


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda: weisz_prater(1.0, 0.0, 1e-5, 1.0), "particle_radius_m"),
        (lambda: mears_external_mass(1.0, 1e-3, -1.0, 0.1, 1.0), "reaction_order"),
        (lambda: mears_external_heat(1.0, 1e-3, 1.0, 1.0, 0.0, 500.0), "coefficient"),
        (lambda: anderson_internal_heat(math.nan, 1e-3, 1.0, 1.0, 1.0, 500.0), "rate"),
    ],
)  # type: ignore[untyped-decorator]
def test_invalid_physical_inputs_fail(call: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        call()  # type: ignore[operator]


def test_zero_order_mears_mass_has_zero_local_sensitivity() -> None:
    result = mears_external_mass(100.0, 1.0e-3, 0.0, 0.01, 1.0)
    assert result.value == 0.0
    assert result.status is ScreeningStatus.PASS


def test_published_mears_mass_supplement_benchmark() -> None:
    """Reproduce RSC C5CY00934K supplementary Mears calculation (700 C case)."""

    mass_rate = 1.014e-4  # mol kgcat^-1 s^-1 (= 1.014e-7 kmol kgcat^-1 s^-1)
    density = 1099.2  # kgcat m^-3
    result = mears_external_mass(
        mass_rate * density,
        1.5e-4,
        6.0,
        0.289,
        8.878,
    )
    assert result.value == pytest.approx(3.910e-5, rel=2e-4)
