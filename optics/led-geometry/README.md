# LED Angle Geometry

## Simple under-slide geometry

If an LED is at distance `h` below the slide and lateral offset `r`, the illumination numerical aperture is approximately:

```text
NA_illum ≈ sin(theta) = r / sqrt(r^2 + h^2)
```

Solve for offset:

```text
r = h * NA_illum / sqrt(1 - NA_illum^2)
```

Example target range:

```text
NA_illum = 0.25 ... 0.40
```

## Design rule

Place red and green LEDs symmetrically across the optical axis. Prefer orienting the red/green axis perpendicular to scan direction so table motion does not mimic the autofocus shift axis.

If scanning along X, place red/green along Y.

## Mechanical requirements

- Adjustable LED lateral offset.
- Adjustable LED-to-slide distance or replaceable spacers.
- Stable mount with no vibration.
- Access for diffuser/collimator experiments.
- Ability to block or disable individual channels.

## Current prototype record

The current red/green oblique AF pair is a `20x`-objective prototype:

- red/green LED rated current: 100 mA per LED;
- lateral offset from optical center: 10 mm;
- distance from tissue plane: 35 mm;
- placement angle: 16 degrees.

The `40x` objective requires a different red/green pair and a separate geometry
record. Do not reuse the `20x` offset, angle or calibration IDs for `40x`.
