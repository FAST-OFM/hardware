# Hardware modification index

The custom linear stage predates this integration and its contributor remains
anonymous. Alexander Fridman's released work begins with controller/motion
integration and includes the illumination and RG-focus hardware interfaces
described below.

This repository documents the hardware portions of:

- `WP-1 MOTION`: NEMA 11 motors, lead-screw kinematics and MKS Robin Mini V2.0
  integration.
- `WP-2 ILLUMINATION`: Arduino-compatible PWM brightness control, MKS timing
  gates, LED-driver requirements and illumination geometry.
- `WP-3 RG-FOCUS`: red/green illumination geometry and the physical assumptions
  behind RG autofocus.
- `FUTURE-001`: camera-trigger and synchronization research for a future 4K
  global-shutter system; this is not a verified release capability.

For this clean release, a machine-specific observed pin record was added and
the older `PB13` WHITE-gate candidate was explicitly separated from the `PB14`
configuration used by the accepted prototype.
