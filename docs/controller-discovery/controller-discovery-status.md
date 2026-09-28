# Controller Discovery Status

Status: docs-only hardware discovery summary. This document does not approve
firmware flashing, GPIO toggling, motion, camera triggering, LED driving,
serial control, network control or hardware tests.

## Known From Current Docs

- The current controller discovery is still open for the MKS/Kingroon board
  context. Do not treat any partial mapping as a complete board definition.
- The current documented controller baseline names an MKS Robin Mini V2.0,
  PCB code `M-M-B-A-00526`, with STM32F103-family MCU evidence from the
  current Klipper deployment.
- The current documented mechanics use NEMA 11 motors.
- The current documented stepper drivers are A4988. This is documentation
  status only; it is not sensorless-homing capability.
- X/Y screw pitch is documented as 2 mm per revolution.
- Z screw pitch is documented as 0.5 mm per revolution.

## Prior Discovery Observations

These signals are observed-by-prior-test or documented from existing discovery
docs. They are not universal board truth and must not be copied into a generic
MKS/Kingroon board profile without review:

- `PD6` / E0_STEP: exercised as the current non-axis trigger/sync signaling
  path and candidate camera-trigger path.
- `PA9` / WiFi TXD1: observed current no-load green LED gate mapping.
- `PA10` / WiFi RXD1: observed current no-load red LED gate mapping.
- `PB13` / TC1 SCK: observed current no-load white LED gate mapping.
- Current 20x red/green AF LED geometry: 100 mA-class LEDs, 10 mm lateral
  offset from optical center, 35 mm from tissue plane and 16 degree placement
  angle.

## Known Absent Or Not Verified

- Homing is currently absent on the MKS setup. Existing Klipper endstop pin
  assignments are candidates only, not proof of working homing.
- V1 bring-up may use an explicitly approved manual-centered bounded test mode
  without homing: X/Y `+/-10 mm` from the manual center, conservative speed and
  acceleration, no homing commands, and Z motion only inside a separately
  approved autofocus search range after manual focus setup. This does not
  satisfy normal scan homing requirements.
- The current A4988 setup has no documented sensorless-homing feedback path.
- Future Pico/RP2040 driver-assisted or sensorless homing remains an
  evaluation topic. It requires exact board, driver, feedback interface,
  current-limit and safe homing evidence before any motion test.

## Unknowns

- Exact MKS/Kingroon board variant relationship and final board profile state.
- Rail budgets and safe available current for controller-powered loads.
- Stepper current limits, Vref/current-limit settings and thermal margins.
- Pin electrical details: voltage levels, reset/default states, drive strength,
  protection, pull-ups/pull-downs and load tolerance.
- Final camera trigger electrical compatibility and exposure timing.
- Loaded LED strobe behavior, current limiting and driver capability.
- 40x red/green AF LED pair, angle, intensity limits and calibration records.
- Spare GPIO availability and electrical safety.
- Firmware flashing/debug flow for the exact target board.

## Next Safe Docs-Only Tasks

- Cross-reference this summary from the owning hardware discovery docs if it
  becomes the canonical current-status page.
- Convert the known baseline into a draft board worksheet with each field
  tagged as documented, candidate, observed-by-prior-test or unknown.
- Link each known item to its source doc or evidence note.
- Keep Pico/RP2040 sensorless homing in the feasibility document until exact
  driver feedback evidence exists.
- Record unknown rail/current/pin-electrical details as blockers, not guessed
  values.

No firmware, hardware, network, Pi, MKS, GPIO, motor, LED, camera, serial,
flashing, probing or live-controller action is approved by these tasks.
