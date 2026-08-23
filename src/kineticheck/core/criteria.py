"""Authoritative transport-limitation screening equations.

All functions take SI magnitudes and return a dimensionless :class:`CriterionResult`.
No property correlation is silently applied: transfer coefficients, diffusivity, and
thermal conductivity are supplied by the researcher.
"""

from __future__ import annotations

import math

from kineticheck.models import CriterionResult, ScreeningStatus

WEISZ_PRATER_DEFAULT_THRESHOLD = 0.30
MEARS_DEFAULT_THRESHOLD = 0.15
ANDERSON_DEFAULT_THRESHOLD = 0.75
GAS_CONSTANT_J_MOL_K = 8.31446261815324

WEISZ_PRATER_REFERENCE = (
    "P. B. Weisz and C. D. Prater, Advances in Catalysis 6 (1954) 143-196, "
    "doi:10.1016/S0360-0564(08)60390-9; threshold convention reviewed by "
    "D. E. Mears, Ind. Eng. Chem. Process Des. Dev. 10 (1971) 541-547, "
    "doi:10.1021/i260040a020."
)
MEARS_MASS_REFERENCE = (
    "D. E. Mears, Ind. Eng. Chem. Process Des. Dev. 10 (1971) 541-547, "
    "doi:10.1021/i260040a020, Eq. 17 convention."
)
MEARS_HEAT_REFERENCE = (
    "D. E. Mears, Journal of Catalysis 20 (1971) 127-131, doi:10.1016/0021-9517(71)90073-X."
)
ANDERSON_REFERENCE = (
    "J. B. Anderson, Chemical Engineering Science 18 (1963) 147-148, "
    "A criterion for isothermal behavior of a catalyst pellet."
)


def _finite_nonnegative(name: str, value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and non-negative")
    return value


def _finite_positive(name: str, value: float) -> float:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _result(
    *,
    criterion: str,
    symbol: str,
    value: float,
    threshold: float,
    equation: str,
    convention: str,
    reference: str,
    assumptions: tuple[str, ...],
) -> CriterionResult:
    _finite_nonnegative("criterion value", value)
    _finite_positive("threshold", threshold)
    below = value < threshold and not math.isclose(value, threshold, rel_tol=1e-12)
    status = ScreeningStatus.PASS if below else ScreeningStatus.FAIL
    return CriterionResult(
        criterion=criterion,
        symbol=symbol,
        value=value,
        threshold=threshold,
        status=status,
        equation=equation,
        convention=convention,
        reference=reference,
        assumptions=assumptions,
    )


def weisz_prater(
    volumetric_rate_mol_m3_s: float,
    particle_radius_m: float,
    effective_diffusivity_m2_s: float,
    surface_concentration_mol_m3: float,
    *,
    threshold: float = WEISZ_PRATER_DEFAULT_THRESHOLD,
) -> CriterionResult:
    """Screen intraparticle mass transfer using the observable Weisz-Prater modulus."""

    rate = _finite_nonnegative("volumetric_rate_mol_m3_s", volumetric_rate_mol_m3_s)
    radius = _finite_positive("particle_radius_m", particle_radius_m)
    diffusivity = _finite_positive("effective_diffusivity_m2_s", effective_diffusivity_m2_s)
    concentration = _finite_positive("surface_concentration_mol_m3", surface_concentration_mol_m3)
    value = rate * radius**2 / (diffusivity * concentration)
    return _result(
        criterion="Weisz-Prater internal mass transfer",
        symbol="C_WP",
        value=value,
        threshold=threshold,
        equation="C_WP = |r_obs,V| R_p^2 / (D_eff C_A,s)",
        convention=(
            "Observed rate per apparent pellet volume and pellet radius are used. The default "
            "C_WP < 0.30 screen is a declared conservative convention, not a universal boundary; "
            "order-specific 5% criteria differ in the literature."
        ),
        reference=WEISZ_PRATER_REFERENCE,
        assumptions=(
            "Steady porous-pellet screening with meaningful effective diffusivity.",
            "C_A,s is the external pellet-surface concentration, not silently the bulk value.",
            "Strong product inhibition or unusual rate laws may invalidate this screen.",
        ),
    )


def mears_external_mass(
    volumetric_rate_mol_m3_s: float,
    particle_radius_m: float,
    absolute_reaction_order: float,
    mass_transfer_coefficient_m_s: float,
    bulk_concentration_mol_m3: float,
    *,
    threshold: float = MEARS_DEFAULT_THRESHOLD,
) -> CriterionResult:
    """Screen gas-particle film concentration gradients using Mears' criterion."""

    rate = _finite_nonnegative("volumetric_rate_mol_m3_s", volumetric_rate_mol_m3_s)
    radius = _finite_positive("particle_radius_m", particle_radius_m)
    order = _finite_nonnegative("absolute_reaction_order", absolute_reaction_order)
    coefficient = _finite_positive("mass_transfer_coefficient_m_s", mass_transfer_coefficient_m_s)
    concentration = _finite_positive("bulk_concentration_mol_m3", bulk_concentration_mol_m3)
    value = rate * radius * order / (coefficient * concentration)
    return _result(
        criterion="Mears external mass transfer",
        symbol="C_MM",
        value=value,
        threshold=threshold,
        equation="C_MM = |r_obs,V| R_p |n| / (k_c C_A,b)",
        convention=(
            "The reaction-order magnitude is placed in the numerator and compared with 0.15, "
            "equivalent to the literature form without n compared with 0.15/n."
        ),
        reference=MEARS_MASS_REFERENCE,
        assumptions=(
            "Local power-law concentration sensitivity is represented by |n|.",
            "k_c and C_A,b apply to the same species and operating point.",
            "Observed rate is expressed per apparent pellet volume.",
        ),
    )


def mears_external_heat(
    volumetric_rate_mol_m3_s: float,
    particle_radius_m: float,
    reaction_enthalpy_j_mol: float,
    activation_energy_j_mol: float,
    heat_transfer_coefficient_w_m2_k: float,
    bulk_temperature_k: float,
    *,
    threshold: float = MEARS_DEFAULT_THRESHOLD,
) -> CriterionResult:
    """Screen fluid-particle film temperature gradients using Mears' heat criterion."""

    rate = _finite_nonnegative("volumetric_rate_mol_m3_s", volumetric_rate_mol_m3_s)
    radius = _finite_positive("particle_radius_m", particle_radius_m)
    enthalpy = abs(_finite_nonnegative("absolute reaction enthalpy", abs(reaction_enthalpy_j_mol)))
    energy = _finite_positive("activation_energy_j_mol", activation_energy_j_mol)
    coefficient = _finite_positive(
        "heat_transfer_coefficient_w_m2_k", heat_transfer_coefficient_w_m2_k
    )
    temperature = _finite_positive("bulk_temperature_k", bulk_temperature_k)
    value = (
        enthalpy * rate * radius * energy / (coefficient * GAS_CONSTANT_J_MOL_K * temperature**2)
    )
    return _result(
        criterion="Mears external heat transfer",
        symbol="C_MH",
        value=value,
        threshold=threshold,
        equation="C_MH = |DeltaH_r| |r_obs,V| R_p E_a / (h R_g T_b^2)",
        convention=(
            "The absolute heat effect and apparent Arrhenius sensitivity are compared with 0.15."
        ),
        reference=MEARS_HEAT_REFERENCE,
        assumptions=(
            "A single apparent activation energy describes local temperature sensitivity.",
            "h is the fluid-particle heat-transfer coefficient at this operating point.",
            "Rate and reaction enthalpy use the same reaction/species stoichiometric basis.",
        ),
    )


def anderson_internal_heat(
    volumetric_rate_mol_m3_s: float,
    particle_radius_m: float,
    reaction_enthalpy_j_mol: float,
    activation_energy_j_mol: float,
    effective_thermal_conductivity_w_m_k: float,
    surface_temperature_k: float,
    *,
    threshold: float = ANDERSON_DEFAULT_THRESHOLD,
) -> CriterionResult:
    """Screen intraparticle temperature gradients using Anderson's criterion."""

    rate = _finite_nonnegative("volumetric_rate_mol_m3_s", volumetric_rate_mol_m3_s)
    radius = _finite_positive("particle_radius_m", particle_radius_m)
    enthalpy = abs(_finite_nonnegative("absolute reaction enthalpy", abs(reaction_enthalpy_j_mol)))
    energy = _finite_positive("activation_energy_j_mol", activation_energy_j_mol)
    conductivity = _finite_positive(
        "effective_thermal_conductivity_w_m_k", effective_thermal_conductivity_w_m_k
    )
    temperature = _finite_positive("surface_temperature_k", surface_temperature_k)
    value = (
        enthalpy
        * rate
        * radius**2
        * energy
        / (conductivity * GAS_CONSTANT_J_MOL_K * temperature**2)
    )
    return _result(
        criterion="Anderson internal heat transfer",
        symbol="C_AH",
        value=value,
        threshold=threshold,
        equation="C_AH = |DeltaH_r| |r_obs,V| R_p^2 E_a / (lambda_eff R_g T_s^2)",
        convention=(
            "The rearranged Anderson 5% isothermality screen is compared with 0.75. Some "
            "secondary sources round the right-hand side; KinetiCheck does not."
        ),
        reference=ANDERSON_REFERENCE,
        assumptions=(
            "Spherical-pellet characteristic radius and effective pellet conductivity are used.",
            "A single apparent activation energy describes local temperature sensitivity.",
            "Rate and reaction enthalpy use the same reaction/species stoichiometric basis.",
        ),
    )
