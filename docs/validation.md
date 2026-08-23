# Validation record

## Hand benchmark

For `r_obs,V = 2 mol m^-3 s^-1`, `R_p = 1e-3 m`, `D_eff = 1e-5 m² s^-1`,
`C_A,s = C_A,b = 10 mol m^-3`, `n = 1`, and `k_c = 0.02 m s^-1`:

- `C_WP = 2 × (1e-3)² / (1e-5 × 10) = 0.02`
- `C_MM = 2 × 1e-3 × 1 / (0.02 × 10) = 0.01`

With `abs(ΔH_r) = 100000 J mol^-1`, `E_a = 80000 J mol^-1`, `h = 250 W m^-2 K^-1`,
`λ_eff = 0.5 W m^-1 K^-1`, and `T = 600 K`:

- `C_MH = 0.021381752007595737`
- `C_AH = 0.010690876003797868`

These values are asserted independently in the regression suite.

## Published operating-point reproductions

The electronic supplementary information for RSC article `C5CY00934K` reports a Mears external-mass
calculation at 700 °C using `r_obs = 1.014e-7 kmol kgcat^-1 s^-1`, a source-labelled bed density
`1099.2 kg m^-3`, radius `1.5e-4 m`, order `6`, `k_c = 0.289 m s^-1`, and
`C_A,b = 8.878e-3 kmol m^-3`. Consistently converting the kmol concentration and rate yields
`C_MM = 3.9097069e-5`, reproducing the reported `3.910e-5`.

- Source: [RSC supplementary PDF](https://www.rsc.org/suppdata/c5/cy/c5cy00934k/c5cy00934k1.pdf)
- Files used: no redistributed file; only the published numerical operating point is encoded in a test
- Validation scope: the external-mass equation and mass-rate/density convention only
- License/checksum: recorded in `public-data-sources.json`; the source PDF is not redistributed

Two additional catalytic systems are now exercised:

- `KC-PUB-002`, acetic-acid HDO over Mo2C: `C_WP=4.9573714e-6` versus `4.96e-6` reported.
- `KC-PUB-003`, glycerol oxidation over three Pt/Cu-CuZrOx catalysts: all three external Mears
  values reproduce within the precision of the source table.

See the [full public-case audit](public-data-validation.md),
[structured source manifest](public-data-sources.json), and
[discrepancy/failure register](public-validation-failures.json). These records explicitly retain
source-equation inconsistencies, unavailable inputs, surface/bulk assumptions, threshold differences,
and characteristic-length conventions instead of forcing numerical agreement.

## Real-data status

Published arithmetic has been validated across three real catalytic systems. This is not raw
instrument-data validation, independent property validation, or a full uncertainty assessment. The
pedagogical CSV remains synthetic, and no publisher PDF is redistributed.
