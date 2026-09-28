# Prototype hardware checkpoint — 2026-09-09

Version: `v0.1.0-prototype.1`  
Evidence type: read-only configuration inspection plus one operator-authorized
bounded scan.  
Product status: R&D prototype; not clinically validated.

This record describes the hardware state actually used by the current
OpenFlexure-based prototype. It does not promote candidate pin mappings to
general board truth, approve firmware flashing, or replace the future
fully-owned hardware architecture.

## Controller and motion observed live

- Controller: MKS Robin Mini V2.0 / STM32F103-family Klipper target.
- Klipper base commit:
  `c707dd19214709dc23684b254a68e3bf69e4cfb3`.
- Runtime version string:
  `v0.13.0-699-gc707dd192-dirty-20260704_130046-pi5`.
- Coordinates are commanded stepper positions, not encoder measurements.
- No verified physical homing is present. The scan used an
  operator-confirmed local zero at the specimen's existing physical position.

| Axis | Step | Direction | Enable | Endstop input | Rotation distance | Microsteps |
| --- | --- | --- | --- | --- | --- | --- |
| X | PE3 | PE2 | !PE4 | !PA15 | 2 mm | 16 |
| Y | PE0 | PB9 | !PE1 | !PA12 | 2 mm | 16 |
| Z | PB5 | !PB4 | !PB8 | !PA11 | 1.0 mm | 16 |

Effective OpenFlexure motion policy observed for the run:

| Axis | Software range | Velocity | Acceleration | Extra bound |
| --- | --- | --- | --- | --- |
| X | -10 to +10 mm | 4 mm/s | 40 mm/s2 | — |
| Y | -12 to +12 mm | 4 mm/s | 40 mm/s2 | — |
| Z | -10 to +20 mm | 0.4 mm/s | 4 mm/s2 | 0.05 mm maximum individual move |

The controller-wide Klipper limits remained 20 mm/s and 50 mm/s2. The stage
adapter used 1000 commanded units/mm, 0.005 mm position tolerance and 0.3 s
push wait.

## Illumination observed live

Active Klipper gate assignments were:

| Channel | Active pin |
| --- | --- |
| Green | PA9 |
| Red | PA10 |
| White | PB14 |

The active white output is PB14. The installed Klipper configuration still
contains obsolete macros named `SCANNER_AF_WINDOW_SAFE_OFF` and
`SCANNER_AF_WINDOW_TEST` that refer to the old `led_white_tc1` output. Do not
execute those macros until they are corrected and reviewed.

The Arduino Nano-compatible brightness controller reported the deployed
configuration as version 4 with 62.5 kHz PWM. Its saved simultaneous R/G
profile was `RED150/GREEN150/WHITE255`. A newer version 5 source candidate
exists in Git but was not deployed for this checkpoint. No Arduino EEPROM
write or firmware flash was performed.

## 4K specimen run

The operator authorized reuse of the specimen and table position left by the
accepted prior scan. The adaptive spiral planner used a 7.5 mm centre-radius
limit, 15 percent overlap, background skip, simultaneous R/G autofocus and
bounded sparse focus prediction. The limit is a planning envelope, not the
dimensions of the retained mosaic.

- 132 commanded field positions visited.
- 97 full-resolution 4056 x 3040 JPEG fields saved.
- 35 background fields skipped before autofocus/capture.
- 30 saved fields used hardware simultaneous R/G autofocus.
- 67 saved fields used bounded sparse plane prediction.
- Acquisition duration: 572 s.
- Saved field centres spanned 8.808 mm in X and 13.200 mm in Y.
- With the calibrated field span, the retained fields' axis-aligned bounding
  footprint was approximately 10.108 mm × 14.179 mm; this does not imply that
  the whole rectangle was populated.
- The stage returned to commanded `(0, 0, 0)` before release.

After all file processing, WHITE, RED and GREEN were verified off. X, Y and Z
motors were disabled. The local reference is therefore invalid; a fresh
operator-confirmed zero is required before any later motion.

## Evidence boundary

This checkpoint records an operating prototype, not a completed safety case.
It does not resolve electrical unknowns, implement mandatory production
homing, verify stepper position independently, validate scale accuracy, or
authorize diagnostic use.
