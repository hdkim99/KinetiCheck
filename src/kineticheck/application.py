"""Application service connecting typed units to the scientific core."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from kineticheck.core import (
    anderson_internal_heat,
    mears_external_heat,
    mears_external_mass,
    weisz_prater,
)
from kineticheck.models import CriterionResult, ScreeningReport
from kineticheck.units import RateBasis, convert, normalize_rate


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return cast(Mapping[str, object], value)


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    return float(value)


def _optional_number(value: object, name: str) -> float | None:
    if value is None:
        return None
    return _number(value, name)


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _quantity(payload: object, target: str, name: str) -> float:
    quantity = _mapping(payload, name)
    return convert(
        _number(quantity.get("value"), f"{name}.value"),
        _text(quantity.get("unit"), f"{name}.unit"),
        target,
        name=name,
    )


def _threshold(payload: Mapping[str, object]) -> dict[str, float]:
    raw = payload.get("threshold")
    return {} if raw is None else {"threshold": _number(raw, "threshold")}


def evaluate_mapping(payload: Mapping[str, object]) -> ScreeningReport:
    """Evaluate one JSON-compatible operating-point mapping.

    Only criteria present under ``criteria`` are evaluated. All conversions to the
    required apparent-pellet-volume rate basis are explicit and recorded.
    """

    run_id_raw = payload.get("run_id", "run")
    run_id = _text(run_id_raw, "run_id")
    rate = _mapping(payload.get("rate"), "rate")
    basis_text = _text(rate.get("basis"), "rate.basis")
    try:
        basis = RateBasis(basis_text)
    except ValueError as error:
        allowed = ", ".join(item.value for item in RateBasis)
        raise ValueError(f"rate.basis must be one of: {allowed}") from error

    density_payload = rate.get("pellet_density")
    density_value: float | None = None
    density_unit = "kg / meter ** 3"
    if density_payload is not None:
        density = _mapping(density_payload, "rate.pellet_density")
        density_value = _number(density.get("value"), "rate.pellet_density.value")
        density_unit = _text(density.get("unit"), "rate.pellet_density.unit")
    conversion = normalize_rate(
        _number(rate.get("value"), "rate.value"),
        _text(rate.get("unit"), "rate.unit"),
        basis,
        pellet_density_value=density_value,
        pellet_density_unit=density_unit,
        bed_void_fraction=_optional_number(rate.get("bed_void_fraction"), "rate.bed_void_fraction"),
    )
    radius = _quantity(payload.get("particle_radius"), "meter", "particle_radius")
    criteria = _mapping(payload.get("criteria"), "criteria")
    results: list[CriterionResult] = []
    warnings: list[str] = []

    wp_raw = criteria.get("weisz_prater")
    if wp_raw is not None:
        wp = _mapping(wp_raw, "criteria.weisz_prater")
        results.append(
            weisz_prater(
                conversion.value_mol_m3_s,
                radius,
                _quantity(
                    wp.get("effective_diffusivity"),
                    "meter ** 2 / second",
                    "effective_diffusivity",
                ),
                _quantity(
                    wp.get("surface_concentration"),
                    "mol / meter ** 3",
                    "surface_concentration",
                ),
                **_threshold(wp),
            )
        )
        if wp.get("surface_concentration_assumed_bulk") is True:
            warnings.append(
                "Weisz-Prater surface concentration was declared equal to the bulk value; "
                "this assumes a negligible external concentration gradient."
            )

    mm_raw = criteria.get("mears_mass")
    if mm_raw is not None:
        mm = _mapping(mm_raw, "criteria.mears_mass")
        results.append(
            mears_external_mass(
                conversion.value_mol_m3_s,
                radius,
                abs(_number(mm.get("reaction_order"), "reaction_order")),
                _quantity(
                    mm.get("mass_transfer_coefficient"),
                    "meter / second",
                    "mass_transfer_coefficient",
                ),
                _quantity(
                    mm.get("bulk_concentration"),
                    "mol / meter ** 3",
                    "bulk_concentration",
                ),
                **_threshold(mm),
            )
        )

    mh_raw = criteria.get("mears_heat")
    if mh_raw is not None:
        mh = _mapping(mh_raw, "criteria.mears_heat")
        results.append(
            mears_external_heat(
                conversion.value_mol_m3_s,
                radius,
                _quantity(mh.get("reaction_enthalpy"), "joule / mol", "reaction_enthalpy"),
                _quantity(mh.get("activation_energy"), "joule / mol", "activation_energy"),
                _quantity(
                    mh.get("heat_transfer_coefficient"),
                    "watt / meter ** 2 / kelvin",
                    "heat_transfer_coefficient",
                ),
                _quantity(mh.get("bulk_temperature"), "kelvin", "bulk_temperature"),
                **_threshold(mh),
            )
        )

    ah_raw = criteria.get("anderson_heat")
    if ah_raw is not None:
        ah = _mapping(ah_raw, "criteria.anderson_heat")
        results.append(
            anderson_internal_heat(
                conversion.value_mol_m3_s,
                radius,
                _quantity(ah.get("reaction_enthalpy"), "joule / mol", "reaction_enthalpy"),
                _quantity(ah.get("activation_energy"), "joule / mol", "activation_energy"),
                _quantity(
                    ah.get("effective_thermal_conductivity"),
                    "watt / meter / kelvin",
                    "effective_thermal_conductivity",
                ),
                _quantity(ah.get("surface_temperature"), "kelvin", "surface_temperature"),
                **_threshold(ah),
            )
        )

    if not results:
        warnings.append("No supported criterion was selected.")
    return ScreeningReport(
        run_id=run_id,
        volumetric_rate_mol_m3_s=conversion.value_mol_m3_s,
        rate_conversion=conversion.description,
        results=tuple(results),
        warnings=tuple(warnings),
    )
