# Batch schema

Input is UTF-8 CSV or XLSX with one header row. Unit columns accept Pint expressions. Blank criterion
groups are not evaluated; if any value in a prefix group is present, all required values for that
criterion must be present.

Common required columns:

- `run_id`
- `rate_value`, `rate_unit`, `rate_basis`
- `particle_radius_value`, `particle_radius_unit`

Rate-basis additions:

- `mass_catalyst`: `pellet_density_value`, `pellet_density_unit`
- `pellet_volume`: no conversion property
- `bed_volume`: `bed_void_fraction`

Criterion groups:

- `wp_effective_diffusivity_{value,unit}`, `wp_surface_concentration_{value,unit}`,
  optional `wp_threshold`
- `mm_reaction_order`, `mm_mass_transfer_coefficient_{value,unit}`,
  `mm_bulk_concentration_{value,unit}`, optional `mm_threshold`
- `mh_reaction_enthalpy_{value,unit}`, `mh_activation_energy_{value,unit}`,
  `mh_heat_transfer_coefficient_{value,unit}`, `mh_bulk_temperature_{value,unit}`,
  optional `mh_threshold`
- `ah_reaction_enthalpy_{value,unit}`, `ah_activation_energy_{value,unit}`,
  `ah_effective_thermal_conductivity_{value,unit}`, `ah_surface_temperature_{value,unit}`,
  optional `ah_threshold`

See [the complete example](../examples/operating_points.csv). Exported CSV/XLSX contains every
dimensionless value, threshold, per-criterion status, overall status, interpretation, rate conversion,
and warnings.
