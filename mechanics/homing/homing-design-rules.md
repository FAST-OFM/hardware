# Homing Design Rules

## Requirements

- X/Y/Z homing switches or equivalent reference sensors.
- Repeatability test for every axis.
- Backoff and re-approach sequence.
- Homing failure timeout.
- Safe Z policy before XY motion near slide/objective.

## Coordinate systems

- Machine coordinates: after homing.
- Slide coordinates: relative to slide holder/reference.
- ROI coordinates: scan plan inside slide/tissue mask.

## Guardrail

Do not start a physical scan unless required axes are homed or the system is explicitly in simulator mode.
