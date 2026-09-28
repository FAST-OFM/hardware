# Homing Readiness Evidence

Status: offline evidence scaffold for issue 11. This document does not approve
firmware flashing, GPIO toggling, motor enable, axis motion, hard-stop homing or
sensorless homing.

Current physical homing is not implemented in checked-in scanner-hardware
evidence. Future Pico or sync-board work may support switch-based, sensor-based
or driver-feedback homing, but that remains a future capability until the
evidence below is recorded and reviewed.

No checked-in evidence in this repository establishes that the current
MKS/A4988 hardware path can detect end of travel or expose stall/endstop
feedback suitable for homing. Treat sensorless homing on that path as unknown,
not available, unless a reviewed board/driver datasheet and firmware path prove
otherwise.

## Evidence Fields

Record these fields before changing any homing readiness status from unknown to
known:

| Evidence area | Required fields |
|---|---|
| Controller identity | Exact board, board revision, scanner variant, MCU, firmware base and source of each fact. |
| Driver capability | Driver model per axis, driver package or module, datasheet reference, current-limit or Vref setting, thermal margin, and whether any diagnostic/stall feedback exists. |
| Endstop inputs | Input pin per axis, connector/wiring path, active polarity, pull-up or pull-down behavior, voltage tolerance, debounce/noise plan and strain relief. |
| Homing source | Selected source per axis: physical switch, non-contact sensor, encoder/index, driver feedback or not supported. |
| Sensorless feasibility | Feedback mechanism, exposed pin/register, firmware support, speed/current range, threshold configuration, false-positive risk, false-negative risk and hard-stop force risk. |
| Safe limits | Reduced current, reduced speed, acceleration limit, travel envelope, timeout, backoff distance and emergency stop or power-off path. |
| Z-specific review | Objective/slide/coverslip clearance, fixture clearance, direction convention and independent approval before any Z motion. |
| Approval | Reviewer, date, exact evidence refs, permitted test scope and explicit prohibition of out-of-scope live actions. |

Unknown hardware values must remain unknown. Do not fill gaps with nominal board
defaults, firmware examples, vendor assumptions or behavior observed on a
different controller.

## No-Motion Test Prerequisites

A no-motion homing readiness review may only inspect documents, photos,
datasheets, disconnected wiring, unpowered continuity where separately approved,
and static evidence. It must not energize motors, toggle GPIO, alter firmware,
configure drivers, issue serial commands to a live controller or move an axis.

Required prerequisites:

- Exact controller and driver identity evidence is recorded.
- Candidate endstop and driver-feedback interfaces are identified from reviewed
  sources.
- Rail voltage and input/output tolerance evidence is recorded.
- Boot/reset output states are known or the test remains fully unpowered and
  disconnected from live control.
- Test points and measurement method are documented.
- Common-reference or isolation plan is documented for any future powered
  measurement.
- Explicit reviewer approval says the test is no-motion only.

## One-Axis Low-Speed Test Prerequisites

Do not run a one-axis low-speed test from this document. The list below is the
minimum evidence required before a separate reviewed test plan can be written.

- One axis is selected; all other axes remain disabled or mechanically blocked
  from unintended motion.
- Step, direction, enable and endstop or homing input mapping for the selected
  axis are verified.
- Driver model, current limit, Vref and thermal margin are recorded.
- Reduced speed, acceleration, current, travel distance and timeout limits are
  recorded.
- Direction convention and expected safe travel direction are recorded.
- Endstop or feedback behavior can be observed without relying on a hard stop as
  the first proof of detection.
- Emergency stop or power-off path is tested without axis motion.
- Z is excluded unless a separate slide/objective collision review approves it.
- Reviewer approval names the exact axis and prohibits homing any other axis.

## Evidence Status File

Use `evidence/homing-readiness-evidence-status.example.json` as the structured
status template. The example intentionally keeps readiness, endstop inputs,
driver feedback, sensorless feasibility and test approvals unknown until real
evidence is added.
