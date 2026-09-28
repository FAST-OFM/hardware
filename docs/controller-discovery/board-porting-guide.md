# Board Porting Guide

Status: docs-only guide. This document does not approve firmware flashing,
GPIO toggling, LED driving, camera triggering, motor enable, axis motion,
homing, serial control, network control or hardware tests.

## Board profile fields

- board name and revision;
- MCU type;
- flashing/debug method;
- X/Y/Z step/dir/enable pins;
- endstop pins;
- camera trigger output pin;
- LED gate pins;
- diagnostics pins;
- voltage levels;
- driver type and configuration method;
- known risks.

## Bring-up steps

Each step below requires the matching evidence-status unknowns to be resolved
and a reviewed stage-specific approval. If a required value is unknown, keep it
unknown and stop at the prior docs-only stage.

1. Identify board and MCU from reviewed evidence.
2. Confirm flashing/debug path and rollback without live output authority.
3. Observe or toggle diagnostic GPIO only after no-motion electrical approval.
4. Test LED gates only through the LED no-guess gate: no actual LEDs, no
   nonzero current setpoint and no controller-board LED rail use until LED part,
   current limit, rail budget, output type and boot/reset state are known.
5. Generate a camera trigger dummy signal only after trigger voltage, polarity,
   output type, protection and disconnected dummy-signal plan are known.
6. Move one axis slowly only after selected-axis step/dir/enable mapping,
   driver current limit, travel envelope, emergency stop path and approval are
   recorded.
7. Test homing inputs only after the selected homing source, endstop or feedback
   input, polarity, pull behavior, timeout, safe limits and approval are
   recorded. Current scanner status is no limit switches connected and homing
   disabled/config-gated.
8. Run a position-indexed trigger test only after the referenced LED, trigger,
   motion and homing stages have their own approvals, or mark the run
   simulator/dry-run only.
