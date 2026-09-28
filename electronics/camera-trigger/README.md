# Camera Trigger Interface

## Goal

Convert MCU trigger output to the electrical level required by the camera.

## Requirements

- Configurable polarity.
- Pulse width support.
- Protection against overvoltage.
- Optional optocoupler or buffer if needed.
- Oscilloscope test point.

## No-Guess Evidence Gate

Do not connect a camera trigger input or drive a live trigger output from
controller firmware until the evidence status file records the required fields
for the exact target camera and trigger circuit:

- trigger input voltage requirement;
- active polarity;
- minimum and maximum pulse width;
- trigger output type and voltage domain;
- source, sink, push-pull, open-drain, optocoupled, or buffered behavior;
- protection, level-shifter, buffer, or optocoupler design;
- boot/reset waveform with the camera disconnected;
- oscilloscope test point and dummy-signal plan;
- reviewer approval record.
- for Raspberry Pi HQ Camera XVS use: the exact XVS test point, GND reference,
  sync role, level-shifter output voltage, polarity and pulse-width evidence.

Unknown trigger electrical behavior remains a blocker. Do not infer it from a
controller pin name, firmware assignment, earlier PiCam tests, or a similar
camera model.

## Notes

Current PiCam HQ tests may not represent final Global Shutter hardware-trigger
behavior. Treat early tests as pipeline experiments, not final timing
validation.

For the current V1 HQ Camera path, the intended role is Raspberry Pi HQ Camera
`sync-sink` on the XVS test point. The official Raspberry Pi synchronous
camera documentation describes HQ Camera source/sink roles, XVS/GND solder
points, and `dtoverlay=imx477,always-on,sync-sink` for a sink camera:
<https://www.raspberrypi.com/documentation/accessories/camera.html#synchronous-captures>.
The design target is MKS `PD6`/`E0_STEP` through a level shifter from 3.3 V
logic to the camera XVS domain, with an initial 200 us pulse inside the
20-500 us bring-up range. Do not connect this to the camera until the
camera-side waveform, polarity and boot/reset inactive state are verified with
the camera disconnected.
