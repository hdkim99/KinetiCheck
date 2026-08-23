"""Pint-backed unit conversion and explicit rate-basis handling."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from pint import UnitRegistry
from pint.errors import DimensionalityError, UndefinedUnitError

ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)


class RateBasis(str, Enum):
    MASS_CATALYST = "mass_catalyst"
    PELLET_VOLUME = "pellet_volume"
    BED_VOLUME = "bed_volume"


@dataclass(frozen=True)
class RateConversion:
    value_mol_m3_s: float
    description: str


def convert(value: float, unit: str, target: str, *, name: str) -> float:
    """Convert a finite quantity, preserving dimensional checks."""

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    try:
        converted = (value * ureg(unit)).to(target).magnitude
    except (DimensionalityError, UndefinedUnitError) as error:
        raise ValueError(
            f"invalid unit for {name}: {unit!r}; expected compatibility with {target}"
        ) from error
    return float(converted)


def normalize_rate(
    value: float,
    unit: str,
    basis: RateBasis,
    *,
    pellet_density_value: float | None = None,
    pellet_density_unit: str = "kg / meter ** 3",
    bed_void_fraction: float | None = None,
) -> RateConversion:
    """Convert an observed rate to mol/(m3 apparent pellet s), explicitly by basis."""

    if value < 0.0:
        raise ValueError("observed rate magnitude must be non-negative")
    if basis is RateBasis.PELLET_VOLUME:
        rate = convert(value, unit, "mol / meter ** 3 / second", name="observed rate")
        return RateConversion(rate, "pellet-volume rate supplied directly")
    if basis is RateBasis.MASS_CATALYST:
        mass_rate = convert(value, unit, "mol / kilogram / second", name="observed rate")
        if pellet_density_value is None:
            raise ValueError("pellet_density is required for a mass-catalyst rate basis")
        density = convert(
            pellet_density_value,
            pellet_density_unit,
            "kilogram / meter ** 3",
            name="apparent pellet density",
        )
        if density <= 0.0:
            raise ValueError("apparent pellet density must be positive")
        return RateConversion(
            mass_rate * density,
            "mass-catalyst rate multiplied by apparent pellet density",
        )
    bed_rate = convert(value, unit, "mol / meter ** 3 / second", name="observed rate")
    if bed_void_fraction is None:
        raise ValueError("bed_void_fraction is required for a bed-volume rate basis")
    if not 0.0 <= bed_void_fraction < 1.0:
        raise ValueError("bed_void_fraction must satisfy 0 <= epsilon_b < 1")
    solid_fraction = 1.0 - bed_void_fraction
    return RateConversion(
        bed_rate / solid_fraction,
        "bed-volume rate divided by explicit bed solid fraction (1 - bed_void_fraction)",
    )
