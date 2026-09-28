# MKS Robin Mini V2 Scanner Safe Test Plan

Status: scaffold only. No hardware test is approved by this document.

This plan records the gated order required before this board profile can move
past `pinmap_candidate`. It is not permission to perform any step.

Pi startup hardware evidence prerequisites are tracked separately in
`../../evidence/pi-startup-hardware-evidence-status.example.json` and
`../../docs/pi-startup-hardware-evidence-prerequisites.md`. Those gates must
remain prohibited while their referenced entries are unknown.

## Current Allowed Use

- Documentation review.
- Simulator-only firmware paths.
- Offline validation of docs/data.
- Stage 0/Stage 1 software-only proposal drafting where
  `approved=false`, `executed=false`, `hardware_access=software_only`,
  `output_mode=none` and approval evidence refs are not yet present.

## Current Procedure Proposals

The checked-in Stage 0 read-only inspection and Stage 1 dummy/no-load preflight
records in `../../evidence/controller-board-discovery-evidence-status.example.json`
are proposals only. They preserve the current candidate/unknown state and do
not approve no-load output, dummy-load connection, LED output, camera trigger,
motion, homing, firmware flashing, GPIO toggling, serial access or network
live-controller access.

Before either proposal can be executed, a human approval record must identify
the exact stage, scope, reviewer, date, allowed no-output actions, stop
conditions and evidence refs. Stage 1 preflight remains a no-output checklist;
any actual no-load or dummy-load measurement still requires a separate
stage-specific live-action approval.

## V1 Manual-Centered Bounded Test Mode

V1 bring-up may use a separate manual-centered bounded test mode after explicit
issue/PR approval. This mode is not a normal scan workflow and does not satisfy
production homing requirements.

V1 test assumptions:

- The operator manually positions the camera and stage near tissue before the
  test begins.
- X/Y motion is limited to `+/-10 mm` from the manually centered origin.
- Initial X/Y limits are `0.5-1 mm/s` speed and `5-10 mm/s^2` acceleration
  unless the approval names a smaller range.
- Z homing is absent. Z may move only after manual focus setup and only within
  a separately approved autofocus search range.
- Homing commands, hard-stop approaches and endstop proof are forbidden in this
  mode.
- Camera trigger and LED output are separate scopes. White illumination may be
  allowed as a constant manual illumination scope only when its LED current
  limit and live-test approval are recorded.
- Emergency stop uses the Fluidd emergency-stop control plus physical power
  removal as the fallback stop path.

This V1 mode remains blocked until the exact approval records the X/Y envelope,
Z focus-search envelope, speed, acceleration, stop path, disabled homing
commands, lighting scope and camera-trigger scope.

## Current Prohibited Use

- Firmware flashing to the MKS board.
- GPIO toggling on real hardware.
- Step pulse generation.
- Motor driver enable.
- Motor motion or homing.
- Camera trigger connection or camera triggering.
- LED output driving or actual LED connection.
- Serial, network or live-controller control.

## Evidence Required Before No-Motion Electrical Tests

- Exact board variant and MCU part identified.
- Firmware flashing/debug path reviewed.
- Pin voltage levels and input/output tolerance documented.
- Reset/default states for candidate pins documented.
- Common reference or isolation plan reviewed for Raspberry Pi, Arduino, MKS
  controller, LED driver and camera trigger interface.
- Rail voltage and current budgets documented.
- External current limits and dummy-load limits documented.
- Test points identified for candidate GPIO, camera trigger, LED gate and LED
  current sense.

## Evidence Required Before LED Gate Tests

- LED current limits known from measurement or datasheet review.
- LED driver input polarity and fault/default behavior known.
- MKS gate default state verified.
- Arduino PWM boot/reset state verified if the Rev A5 driver is present.
- Dummy load or high-impedance measurement plan reviewed before any actual LED
  connection.

## Evidence Required Before Camera Trigger Tests

- Camera trigger voltage, polarity and pulse-width requirements known.
- Protection, level shifting, buffer or optocoupler design reviewed.
- Oscilloscope test point available.
- Camera disconnected during initial dummy-signal checks.

## Evidence Required Before Motion Or Homing Tests

- X/Y/Z step, direction and enable pins verified.
- Driver type, current limit, Vref and thermal margin documented.
- Endstop or homing input pins verified.
- Axis direction, reduced-current limits, low-speed limits and emergency
  stop/power-off path reviewed.
- Z collision risk reviewed separately.

For the V1 manual-centered bounded test mode, lack of homing inputs is not a
blocker for the bounded non-scan test itself. It remains a blocker for homing
tests and normal scan workflows. The V1 motion gate still requires verified
motion pins for the selected axes, conservative current/speed limits, manual
origin setup, soft travel limits, stop path and explicit approval. Z remains a
separate focus-search scope with its own travel limit.

## Stop Conditions

Stop and return to docs-only status if any expected pin, voltage, reset state,
load behavior, current limit, rail budget, homing input or trigger polarity is
unknown or contradicts the checked-in profile.
