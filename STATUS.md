# Hardware status

Release target: `v0.3.0-prototype.1`
Product status: research prototype; not clinically validated

## Observed on the accepted prototype

- MKS Robin Mini V2.0 / STM32F103-family controller.
- NEMA 11 motion with 2 mm X/Y and 1.0 mm configured Z rotation distance.
- X/Y/Z software pin assignments recorded in
  `boards/mks-robin-mini-v2-scanner/observed-prototype-pins.yaml`.
- GREEN `PA9`, RED `PA10` and WHITE `PB14` illumination gates.
- Arduino Nano-compatible brightness controller and three-channel LED setup.
- Raspberry Pi HQ Camera / Sony IMX477 rolling-shutter capture.

## Unresolved or unverified

- No verified physical homing or encoder feedback.
- Stepper current limits, Vref and thermal margin are not release-qualified.
- Electrical load tolerance, boot/reset levels and protection are incomplete.
- The old `PB13` WHITE-gate candidate is not accepted prototype truth.
- Trigger/level-shifter designs and continuous global-shutter capture are
  experimental/roadmap only.
- The repository does not yet contain a complete, production-ready CAD/BOM
  package for every mechanical and electronic assembly.

An observed software configuration is evidence about one machine; it is not a
generic board pinout or authorization to reproduce the wiring without
measurement.
