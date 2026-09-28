# Two-Color AF LED Geometry

## Default

Use red and green off-axis LEDs placed on opposite sides of the optical axis. For scan along X, prefer placing LEDs along Y so the focus-induced shift is mostly perpendicular to scan motion.

## Geometry

For a simple LED plane below the slide:

```text
NA_illum ≈ r / sqrt(r^2 + h^2)
```

where:

- `h` is LED plane distance to sample;
- `r` is lateral LED offset.

## Calibration dependency

Changing LED position, wavelength, diffuser, condenser or current invalidates AF flat-field and focus curve calibrations.

## Current 20x Prototype Geometry

The current red/green AF prototype geometry is documented for the `20x`
objective only:

- Red and green LED rated current: 100 mA each.
- Lateral offset from optical center: 10 mm.
- LED distance from tissue plane: 35 mm.
- Oblique placement angle: 16 degrees.

This is a measured/current build configuration, not a universal scanner rule.
The project expects stronger red/green LEDs in a later revision.

## 40x Geometry Requirement

The `40x` objective must use a separate red/green LED pair and geometry. Do not
reuse the `20x` LED pair, angle, offset, intensity calibration or focus curve
for `40x`.

A `40x` geometry record must document:

- red and green LED part numbers or explicit unknowns;
- lateral offset and height from the tissue plane;
- oblique angle;
- drive-current limits;
- intensity balance;
- AF flat-field and focus-curve calibration IDs.

## Future variants

The mechanical design should allow testing RG, GR, BG or GB pairs by changing LED assignments or LED board positions.
