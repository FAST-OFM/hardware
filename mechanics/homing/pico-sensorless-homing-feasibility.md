# Pico Sensorless Homing Feasibility

Status: feasibility scaffold, no hardware approval.

This document tracks whether a future Pico-based controller can home axes
using stepper-driver feedback rather than discrete endstop switches.

No firmware flashing, motor motion, hard-stop homing, GPIO toggling or driver
configuration changes are approved by this document.

## Current Known / Unknown

| Item | Status | Notes |
|---|---|---|
| Pico board revision | unknown | Must be read from the physical board or purchase record. |
| Stepper driver model | unknown | Do not assume StallGuard or equivalent support. No checked-in evidence establishes that the current MKS/A4988 path can detect end of travel. |
| Driver feedback signal/register | unknown | Depends on exact driver and firmware base. |
| Firmware base | undecided | Klipper, grblHAL and sync-board fallback remain under evaluation. |
| Current scanner homing | none verified | Existing MKS Robin Mini setup has no verified homing implementation. |

## Sensorless Homing Decision Matrix

| Axis | Candidate? | Default position | Required evidence before motion |
|---|---|---|---|
| X | possible | not approved | Driver model supports feedback; threshold/current/speed plan reviewed; free travel confirmed; hard-stop force risk reviewed. |
| Y | possible | not approved | Same as X; confirm Y mechanics and cable drag do not create false positives. |
| Z | high risk | not approved | Requires separate review because false detection or hard-stop motion can risk slide/objective collision. Prefer physical switch or non-contact/index method unless sensorless behavior is proven safe. |

## Required Evidence

- Exact board revision.
- Exact stepper driver model and datasheet.
- Per-axis driver capability, including whether diagnostic/stall feedback is
  present, electrically exposed and supported by the chosen firmware.
- Endstop or homing input mapping, polarity and electrical behavior for every
  axis.
- Firmware support path for driver feedback:
  - Klipper configuration/MCU support;
  - grblHAL driver/plugin support;
  - or external sync/controller fallback.
- Whether feedback is exposed by pin, UART/SPI register, diagnostic pin or
  firmware-internal state.
- Whether feedback works at the low speeds and currents needed for safe
  microscope-stage homing.
- Whether thresholds are persistent, configurable and axis-specific.
- Safe no-motion review approval before any powered probing or configuration
  changes.
- Separate one-axis low-speed test approval before any motor enable, step pulse
  generation, hard-stop approach or homing attempt.

## No-Motion Review Checklist

- Driver feedback mechanism identified.
- Electrical interface reviewed.
- Current/Vref/current-limit behavior documented.
- Axis mechanical hard-stop reviewed.
- Emergency stop/power-off path identified.
- False positive and false negative risks listed.
- Z-specific collision risk reviewed separately.
- Repeatability experiment plan updated for the selected homing source.

## Risks

- False positive from friction, cable drag, acceleration or vibration.
- False negative causing continued motion into a hard stop.
- Threshold drift with current, speed, temperature or lubrication.
- Different behavior across X/Y/Z mechanics.
- Z collision risk with objective, slide, coverslip or fixture.
- Driver feedback unavailable in the chosen firmware base.

## Feasibility Outcome Values

Use one of these values per axis after evidence is collected:

- `unknown`: insufficient evidence.
- `not_supported`: selected driver/firmware cannot provide usable feedback.
- `bench_only`: useful for diagnostics but not safe enough for homing.
- `candidate_with_limits`: possible with conservative current/speed/threshold
  limits and a separate safe test plan.
- `accepted`: validated by reviewed repeatability and fault tests.

Current outcome for all axes: `unknown`.

## Next Step

Identify the exact Pico board revision and stepper driver model. Do not start
sensorless homing motion tests until those are known and reviewed.
