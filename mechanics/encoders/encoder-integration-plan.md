# Encoder Integration Plan

## Why encoders

Stepper counts are commanded position, not measured position. Linear encoders allow measured coordinate truth and enable lower-overlap coordinate tiling.

## Design now

Even before buying encoders, reserve:

- mechanical mounting surfaces;
- cable paths;
- controller input pins or external counter interface;
- metadata fields;
- calibration schema.

Track readiness with the offline evidence-status artifact at
`evidence/encoder-readiness-evidence-status.example.json`. The artifact is the
source for current non-live unknown/blocker status; it must not be used to fill
in selected parts, electrical levels, pin mappings, calibration constants, or
measured behavior by assumption.

## Modes

1. No encoder: step-indexed.
2. Encoder installed, not triggering: hybrid logging.
3. Encoder used for trigger: encoder-indexed.

## Tests

- encoder pulse simulator;
- hybrid commanded-vs-measured report;
- trigger by encoder count at low speed;
- residual overlap using encoder coordinates.
