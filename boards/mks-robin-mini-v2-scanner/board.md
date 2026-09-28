# MKS Robin Mini V2 Scanner Board Profile

Status: contains both an older docs-only `pinmap_candidate` and a separate
machine-specific observed prototype configuration.

## Which pin file to use

- `observed-prototype-pins.yaml` records the software configuration observed on
  the accepted Fast OFM prototype on 2026-09-09. It includes the active WHITE
  gate on `PB14` and the X/Y/Z motion pins.
- `pins.yaml` preserves an older candidate design profile, including the
  superseded WHITE-gate candidate `PB13`. It is retained as design history and
  must not be used as the accepted machine configuration.

Observed runtime configuration is not the same as generic board validation or
electrical approval. Current limits, loaded behavior, reset state, homing and
encoder feedback remain unresolved.

This profile is bounded to the current scanner MKS Robin Mini V2.0 context. It
does not define a generic MKS Robin Mini V2 board and does not approve firmware
flashing, GPIO toggling, motor motion, camera triggering, LED driving, serial
control, network control, probing or hardware tests.

## Evidence Sources

- `docs/controller-discovery/controller-board-discovery.md`
- `docs/controller-discovery/board-porting-guide.md`
- `docs/controller-discovery/controller-discovery-status.md`
- `electronics/led-driver/rev-a5-arduino-pwm-brightness-controller.md`
- `electronics/camera-trigger/README.md`
- `evidence/rev-a5-evidence-status.example.json`
- `mechanics/homing/README.md`
- `mechanics/homing/pico-sensorless-homing-feasibility.md`

## Profile State

The profile is `pinmap_candidate` because candidate HQ XVS sync and LED gate
pins are documented in checked-in evidence. It is not `pinmap_verified` because
pin electrical details, voltage levels, reset/default states, loaded behavior
and safe output use have not been verified in the checked-in evidence.

Until `pinmap_verified`, follow the firmware restrictions in
`docs/controller-discovery/controller-board-discovery.md`:

- do not emit step pulses on real hardware;
- do not enable motor drivers;
- do not drive LED outputs;
- do not connect the HQ XVS sync output to the camera without the approved
  3.3 V-to-1.8 V level shifter and explicit test approval;
- simulator-only code is allowed.

## Known From Checked-In Docs

| Field | Value | Evidence |
|---|---|---|
| Controller baseline | MKS Robin Mini V2.0 | `docs/controller-discovery/controller-discovery-status.md` |
| PCB code | `M-M-B-A-00526` | `docs/controller-discovery/controller-discovery-status.md` |
| MCU family evidence | STM32F103-family evidence from current Klipper deployment | `docs/controller-discovery/controller-discovery-status.md` |
| Stepper drivers | A4988 | `docs/controller-discovery/controller-discovery-status.md` |
| Current mechanics motor class | NEMA 11 | `docs/controller-discovery/controller-discovery-status.md` |
| X/Y screw pitch | 2 mm per revolution | `docs/controller-discovery/controller-discovery-status.md` |
| Z screw pitch | 0.5 mm per revolution | `docs/controller-discovery/controller-discovery-status.md` |
| Current homing state | none verified on MKS setup | `docs/controller-discovery/controller-discovery-status.md`, `mechanics/homing/README.md` |
| Current homing configuration | disabled/config-gated; no verified homing | `boards/mks-robin-mini-v2-scanner/observed-prototype-pins.yaml`, `evidence/prototype-checkpoint-2026-09-09.md` |
| V1 bounded test mode | manual-centered non-scan test, X/Y `+/-10 mm`; Z only for approved focus-search range | `boards/mks-robin-mini-v2-scanner/safe-test-plan.md`, `docs/hardware-gated-test-procedure-ladder.md` |

These facts are documentation status only. They are not hardware approval.

## Candidate Scanner Signals

These are scanner-context candidates from checked-in evidence. They must not be
treated as universal board truth.

| Signal | Candidate pin / connector | Evidence status | Loaded behavior |
|---|---|---|---|
| HQ XVS sync | `PD6` / `E0_STEP` | documented assignment, 3.3 V at MKS, requires 3.3 V-to-1.8 V level shifter before HQ XVS | unknown |
| Green LED gate | `PA9` / `WiFi TXD1` | documented assignment, positive polarity | unknown |
| Red LED gate | `PA10` / `WiFi RXD1` | documented assignment, positive polarity | unknown |
| White LED gate | `PB13` / `TC1 SCK` | older candidate, superseded for the accepted prototype by observed `PB14` | unknown |

The current discovery status describes these as prior observations or current
assignments, not verified board-profile truth. Do not connect the camera or LEDs
from this profile alone.

## Unknowns Blocking Verification

- Exact MKS/Kingroon board variant relationship and final board profile state.
- Firmware flashing/debug method for the exact target board.
- X/Y/Z step, direction and enable pins for this scanner profile.
- Endstop pins and working homing inputs.
- Future limit-switch connector mapping, polarity and wiring path.
- Pin voltage levels, reset/default states, pull-ups or pull-downs, drive
  strength, protection and load tolerance.
- HQ XVS electrical compatibility after level shifting, polarity at the camera
  interface and exposure timing.
- LED gate behavior under load, current limiting, driver capability and boot or
  reset default state.
- Rail voltage and available current for any controller-powered or external LED
  load.
- Stepper current limits, Vref/current-limit settings and thermal margins.
- Spare GPIO availability and electrical safety.

## Board-Profile Decision

This directory is an evidence container for future firmware work. Firmware may
only consume it in simulator-only paths until the unknowns above are resolved by
new reviewed evidence and the state is raised to `pinmap_verified`.
