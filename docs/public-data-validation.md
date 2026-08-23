# Public research-case validation audit

Audit date: 2026-08-23. Software baseline: KinetiCheck 0.1.0 at
`d4b88a28ffa98f9585de20b37a33af43ee383acc`.

This audit searched published catalytic transport-screening cases before considering any core
change. It found no failure of the released equation or unit contract. Therefore, the scientific core
was not modified and no release was created. The machine-readable source manifest is
[`public-data-sources.json`](public-data-sources.json); the discrepancy/failure register and taxonomy
are in [`public-validation-failures.json`](public-validation-failures.json).

## Accepted numerical replays

### KC-PUB-001 — Mo/HZSM-5 methane dehydroaromatization

The supplement to [doi:10.1039/C5CY00934K](https://doi.org/10.1039/C5CY00934K) gives

`C_MM = r_mass rho_b R n / (k_c C_A,b)`.

At 700 °C and WHSV 750, consistent kmol-to-mol conversion gives

`(1.014e-4)(1099.2)(1.5e-4)(6) / ((0.289)(8.878)) = 3.909706899602532e-5`,

versus `3.910e-5` reported. At WHSV 9000, the same independent calculation gives
`6.387068746418958e-5`, versus `6.387e-5`. The paper labels `rho_b` as catalyst bed density,
whereas the released mass-rate API asks for apparent pellet density. These tests therefore establish
numerical and unit-path reproduction only; they do not resolve that physical rate-basis ambiguity.

### KC-PUB-002 — Mo2C acetic-acid hydrodeoxygenation

The supplement to [doi:10.1039/C8CY00358K](https://doi.org/10.1039/C8CY00358K) lists
`r=1.50e-7 mol gcat^-1 s^-1`, `rho=759 kgcat m^-3`, `dp=2e-6 m`,
`D_eff=8.03e-6 m2 s^-1`, and `C_A,s=2.86e-3 mol m^-3`. With the required conversion
`r=1.50e-4 mol kgcat^-1 s^-1` and `R=dp/2=1e-6 m`, KinetiCheck gives

`C_WP = (1.50e-4)(759)(1e-6)^2 / ((8.03e-6)(2.86e-3))`
`= 4.9573713957275605e-6`,

versus `4.96e-6` reported. The source explicitly assumes the surface concentration equals bulk, so
the fixture declares that assumption and KinetiCheck returns `WARN` despite the criterion passing.

Equations S4-S7 print a surface-area factor `S`, but every corresponding table number is reproduced
only when `S` is omitted after converting the mass rate. For example, including the listed
`S=100e3 m2 kgcat^-1` would give `0.495737`, not `4.96e-6`, and breaks dimensional closure. This is
classified as `SOURCE_INTERNAL_INCONSISTENCY`, not repaired in software. The paper's
Anderson-labelled `Tave/Ts` balance also lacks the activation-energy sensitivity in KinetiCheck's
dimensionless 5% screen and was excluded as a formulation mismatch.

### KC-PUB-003 — Pt/Cu-CuZrOx glycerol oxidation

Supplementary Table 9 of the CC BY 4.0 article
[doi:10.1038/s41467-022-33038-w](https://doi.org/10.1038/s41467-022-33038-w)
supplies three external Mears calculations. Replaying the stated upper secondary-particle sizes gives:

| Catalyst | Reported `C_MM` | KinetiCheck `C_MM` |
|---|---:|---:|
| 0.9% Pt1+Ptn/Cu-CuZrOx | 7.74e-5 | 7.741996382636655e-5 |
| 0.9% Ptn/Cu-CuZrOx | 5.57e-5 | 5.565252990353698e-5 |
| 0.9% PtCu-CuZrOx | 4.31e-5 | 4.308683305466238e-5 |

The table exposes primary size only as `R1 < 1.0e-7 m`. Using that bound does not reproduce the
reported Weisz-Prater values; inversion implies unlisted radii of approximately 2.38 nm. Those rows
are not regression oracles. The external values should also be read as bound-based screens rather
than exact measurements.

## Independent convention audit

| Screen | Released definition audited | Source differences that must remain explicit |
|---|---|---|
| Weisz-Prater | `abs(r_obs,V) R_p^2/(D_eff C_A,s)` | `R_p=d_p/2`; surface is not bulk unless declared; 5% thresholds depend on rate law, while many papers use `<<1`. |
| Mears external mass | `abs(r_obs,V) R_p abs(n)/(k_c C_A,b) < 0.15` | Equivalent to placing `n` on the right as `0.15/n`; published density labels do not always identify pellet versus bed volume. |
| Mears external heat | `abs(DeltaH) abs(r_obs,V) R_p E_a/(h R_g T_b^2) < 0.15` | KinetiCheck declares radius. KC-PUB-006 instead uses `V/A=R/3`, which changes the number by three and is not silently treated as equivalent. |
| Anderson internal heat | `abs(DeltaH) abs(r_obs,V) R_p^2 E_a/(lambda_eff R_g T_s^2) < 0.75` | Direct temperature-rise balances such as `Tave/Ts` are related checks but not the same dimensionless 5% criterion. |

The authoritative lineage remains Weisz and Prater (1954), Mears' 1971 transport review and heat
paper, and Anderson (1963), as cited in [scientific-basis.md](scientific-basis.md). A pass still means
only that the selected criterion did not detect a significant limitation under the supplied inputs.

## Candidates not promoted to validation fixtures

- `KC-PUB-004`, Au/CeO2 ethanol oxidation, DOI `10.1039/C7RE00175D`: an integrity-checked source
  with all convention-defining numerical inputs was not obtained.
- `KC-PUB-005`, VOx/SiO2 propane oxidative dehydrogenation, DOI `10.1039/D4EY00094C`: the main
  article reports `C_WP=1.54e-3` and `C_MM=2.82e-3`, but the ESI input table was not retrievable for
  independent replay during this audit.
- `KC-PUB-006`, cobalt Fischer-Tropsch particle model, DOI `10.1039/C2CY20060K`: retained as a
  characteristic-length diagnostic, not a regression oracle.

## Reproducible workflows

```bash
kineticheck evaluate examples/public_validation/kc-pub-001-mda-mears.json
kineticheck evaluate examples/public_validation/kc-pub-002-acetic-acid-wp.json
kineticheck evaluate examples/public_validation/kc-pub-003-glycerol-mears.json
```

The KC-PUB-001 values also fit the GUI's current mass-rate/single-point scope. The GUI integration
test enters that published point, calls the shared service, verifies `C_MM`, exports JSON, closes the
window, and exits. The GUI does not retrieve papers or infer missing properties.

## Validation boundary

This round validates published arithmetic across three real catalytic systems. It does not constitute
raw-instrument-data validation, independent measurement of diffusivity or transfer coefficients, or
validation of every physical assumption made by the source authors. No source PDF is redistributed.
