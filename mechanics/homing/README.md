# Homing Hardware

## Requirements

- X/Y/Z home switches.
- Mechanically repeatable mounting.
- Cable strain relief.
- Noise-resistant wiring.
- Safe Z homing arrangement to avoid objective/slide collision.

## Experiments

See `scanner-docs/experiments/homing-repeatability-test-plan.md`.

## Readiness Evidence

See `homing-readiness-evidence.md` and
`../../evidence/homing-readiness-evidence-status.example.json` for the bounded
offline evidence fields and live-action gates required before homing readiness
can be treated as known. Current physical homing is not implemented in
checked-in scanner-hardware evidence.

## Sensorless Homing Feasibility

See `pico-sensorless-homing-feasibility.md` for the current no-motion feasibility
matrix. The current MKS/A4988 setup has no verified sensorless-homing feedback
path; future Pico/RP2040 driver-assisted homing requires exact board and driver
evidence before any motion test.
