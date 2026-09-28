# Pi Startup Hardware Evidence Prerequisites

Status: docs-only prerequisite definition for lifting the Pi startup
`hardware_evidence_unknown` blocker.

This document does not approve firmware flashing, GPIO toggling, serial or
network control of a live controller, motor enable, motor motion, homing, LED
driving, camera triggering, probing under controller command, or any live
hardware test.

## Evidence Artifact

The current prerequisite snapshot is:

- `evidence/pi-startup-hardware-evidence-status.example.json`

That file is the source for current unknowns, blockers, and no-live-action
gates. Values marked `unknown` must remain unknown until supporting evidence is
added and the relevant entry is removed from `required_unknowns`.

## Startup Gate

Pi startup must remain in simulator, dry-run, or other non-live mode while the
`pi_startup_hardware_evidence_unknown` blocker is present.

Do not lift the blocker for real hardware until reviewed evidence records:

- exact target controller board revision and variant relationship;
- exact MCU part and voltage domain;
- reviewed flash/debug method and rollback path for the exact target;
- X/Y/Z step, direction, enable, and endstop mappings;
- X/Y/Z homing source, capability, risks, and safe test limits;
- controller, motor, and LED rail voltage/current budgets;
- controller and driver boot/reset output states;
- LED current limits, current-sense path, loaded behavior, and thermal limits;
- camera trigger voltage, polarity, pulse-width, protection, and boot state;
- common reference or isolation plan across Pi, controller, LED driver, and
  camera trigger interface;
- explicit review record approving the exact startup mode.

Candidate LED and trigger pins documented elsewhere remain candidates or prior
observations unless the evidence artifact says otherwise. Do not copy them into
startup live-hardware behavior by assumption.

## No-Live-Action Gates

The evidence artifact defines separate gates for:

- Pi startup real-hardware mode;
- no-motion electrical live tests;
- motion or homing live tests;
- LED live tests;
- camera trigger live tests.

Each gate lists `blocked_by`, `prohibited_actions`, and
`evidence_fields_required`. A gate with `status:
prohibited_by_unknowns` means the listed actions remain prohibited even if a
different subsystem has partial evidence.

## Resolution Rules

- Keep board revision, pins, rails, current limits, homing capability, LED load
  behavior, and trigger behavior unknown until there is direct reviewed
  evidence.
- Do not convert an entry to `known` using placeholders such as `TBD`,
  `unknown`, or assumed values.
- Do not use a Pi startup path to gather the first live hardware evidence.
  Live evidence collection needs its own reviewed gate and stop conditions.
- Motion, homing, LED, and camera trigger approvals are independent. Resolving
  one gate does not approve the others.
- Z motion and Z homing require a separate slide/objective collision review.

## Offline Validation

Run the offline validator after changing evidence files:

```text
python3 scripts/validate_evidence_status.py
```

The validator reads checked-in JSON only. It does not access GPIO, serial
ports, network resources, firmware, or hardware.
