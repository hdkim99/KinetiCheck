# Scientific definitions

KinetiCheck uses the apparent-pellet-volume observed rate `r_obs,V` in every criterion. A rate per
catalyst mass is multiplied by the explicitly supplied apparent pellet density. A rate per bed volume
is divided by the explicitly supplied bed solid fraction, `1 - ε_b`. Bulk density and apparent pellet
density must not be substituted for each other without stating the associated volume basis.

## Weisz–Prater internal mass screen

`C_WP = abs(r_obs,V) R_p² / (D_eff C_A,s)`

The observable modulus originates in P. B. Weisz and C. D. Prater, “Interpretation of Measurements in
Experimental Catalysis,” *Advances in Catalysis* **6** (1954) 143–196,
[doi:10.1016/S0360-0564(08)60390-9](https://doi.org/10.1016/S0360-0564(08)60390-9).

The default `C_WP < 0.30` is declared as a conservative screening convention. It is not universal:
Mears' 1971 review shows that a criterion tied to a 5% effectiveness-factor deviation depends on
reaction order (and can fail for strong product inhibition). EUROKIN, for example, documents `0.08`
for a stated less-than-5% screen and `0.33` for zero order. KinetiCheck therefore records the actual
threshold and permits an explicit override. `C_A,s` means pellet-surface concentration; it is not
silently replaced with bulk concentration.

## Mears external mass screen

`C_MM = abs(r_obs,V) R_p abs(n) / (k_c C_A,b)`

KinetiCheck compares this form with `0.15`. Mears' Eq. 17 is commonly written without `n` on the
left and with `0.15/n` on the right; the two arrangements are algebraically identical for positive
order. The input is called reaction-order magnitude to keep this convention explicit. For zero local
concentration sensitivity, the dimensionless value is zero.

Reference: D. E. Mears, “Tests for Transport Limitations in Experimental Catalytic Reactors,”
*Industrial & Engineering Chemistry Process Design and Development* **10** (1971) 541–547,
[doi:10.1021/i260040a020](https://doi.org/10.1021/i260040a020).

## Mears external heat screen

`C_MH = abs(ΔH_r) abs(r_obs,V) R_p E_a / (h R_g T_b²)`

The default comparison is `< 0.15`. Enthalpy and rate must use the same reaction/species
stoichiometric basis. `h` is supplied for the operating point; KinetiCheck does not silently choose a
Nusselt correlation. The implemented characteristic length is the spherical particle radius
`R_p = d_p/2`. A source that instead inserts `V_p/A_p = R_p/3` is using a numerically different
convention and must not be compared without adjustment; `KC-PUB-006` in the
[public-case audit](public-data-validation.md) demonstrates the factor-of-three consequence.

Reference: D. E. Mears, “Diagnostic Criteria for Heat Transport Limitations in Fixed Bed Reactors,”
*Journal of Catalysis* **20** (1971) 127–131,
[doi:10.1016/0021-9517(71)90073-X](https://doi.org/10.1016/0021-9517(71)90073-X).

## Anderson internal heat screen

`C_AH = abs(ΔH_r) abs(r_obs,V) R_p² E_a / (λ_eff R_g T_s²)`

The rearranged 5% isothermality comparison is `< 0.75`. Some secondary sources round the numerical
constant; KinetiCheck preserves `0.75`. The characteristic length is the radius of the spherical
pellet convention and `λ_eff` is the effective pellet thermal conductivity. A direct parabolic
temperature-rise expression such as `T_ave/T_s` without the activation-energy factor is a related
thermal balance, but it is not this dimensionless 5% rate-deviation screen.

Reference: J. B. Anderson, “A Criterion for Isothermal Behavior of a Catalyst Pellet,” *Chemical
Engineering Science* **18** (1963) 147–148.

## Interpretation boundary

`PASS` means only: “No significant limitation was detected by the selected criterion under the
supplied assumptions and input properties.” It does not mean that intrinsic kinetics were proven.
`FAIL` means that the declared threshold was met or exceeded and transport influence should be
investigated. A point with an explicit assumption warning is `WARN` only when no selected criterion
fails; a failure is never hidden behind a warning.
