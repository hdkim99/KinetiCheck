# Naming and competitive audit

Audit date: 2026-08-23. Search channels: GitHub repository name search, exact owner/repository lookup,
PyPI JSON project lookup (including normalized lowercase form), and general web search for software,
scientific tools, companies, products, GUI frameworks, and Python packages. A single empty GitHub
search was not treated as sufficient.

| Candidate | Assessment | Finding |
|---|---|---|
| IntrinsicCheck | MINOR RISK | No package/repository, but an old Rust compiler internal symbol and strong functional-language proximity to GradientCheck |
| CatRegime | MINOR RISK | No package/repository; unrelated historical commerce domain/user handle and “cat” ambiguity |
| RegimeCheck | HIGH RISK | Exact-name GitHub repository exists |
| KinetiScope | HIGH RISK | Mature Kinetiscope scientific kinetics simulator and unrelated media company dominate results |
| KinetiGuard | MINOR RISK | Exact-name small GitHub project and health-brand-style uses |
| **KinetiCheck** | **CLEAR — selected** | No exact web, GitHub, PyPI, company/product, Qt, or Python-package collision found |
| IntrinsicLens | MINOR RISK | No software collision; likely ophthalmic/lens semantic confusion |
| RateRegime | MINOR RISK | No software collision but phrase is broadly used in scientific prose |
| TransportScreen | MINOR RISK | No scientific package collision; generic UI/component phrase in transport apps |
| RegimeScreen | CLEAR | Available but less directly descriptive of kinetics |
| CatalystRegime | CLEAR | Available but longer and more generic |
| IntriRate | CLEAR | Available but an unnatural abbreviation |
| TransportGuard | CLEAR | Available but scope is excessively broad |
| KineticsGuard | CLEAR | Available but generic and defensive-product sounding |

Selected identifiers:

- Project: `KinetiCheck`
- GitHub repository: `KinetiCheck`
- PyPI candidate: `kineticheck`
- Python import: `kineticheck`

Availability is a point-in-time observation, not a trademark opinion or reservation. PyPI reported
HTTP 404 for `https://pypi.org/pypi/kineticheck/json`; GitHub exact-name search returned zero and
`hdkim99/KinetiCheck` returned 404 before creation.

## Competitive landscape

- Purdue/Dow [GradientCheck](https://engineering.purdue.edu/~catalyst/gradientcheck/grad_history.html)
  is the closest functional competitor and estimates internal/external gradients in a browser.
- [EUROKIN fixed-bed webtool](https://www.eurokin.org/wp-content/uploads/webtool/EUROKIN_fixed-bed_html.htm)
  combines Weisz–Prater and Mears checks with selected correlations.
- DETCHEM provides commercial, higher-fidelity reactor and pellet transport models.
- Small single-equation web calculators cover Weisz–Prater but usually lack reproducible batch,
  basis-conversion, API, and four-criterion exports.

KinetiCheck differentiates itself through explicit rate-basis conversion, no silent property
correlations, machine-readable assumptions/references, CSV/XLSX batch work, a headless API/CLI, and
a lightweight Tk GUI sharing one core.
