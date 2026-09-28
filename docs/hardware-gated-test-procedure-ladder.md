# Hardware-Gated Test Procedure Ladder

Status: procedure definition only. This document does not approve any live
hardware test.

This ladder defines the order and evidence gates for future scanner hardware
bring-up. It does not approve firmware flashing, serial or network control of a
live controller, GPIO toggling, motor enable, motor motion, homing, LED driving,
camera triggering, probing under controller command, or external integrations.

All unknown values must remain unknown until reviewed evidence records the exact
value, source, method, date and approval. Do not fill gaps with nominal board
defaults, vendor examples, firmware assumptions, prior lab habits or behavior
from similar hardware.

This R&D procedure makes no clinical, diagnostic, regulatory, safety-certified
or performance-validated claims.

## Gate Rules

- Stages are sequential. Passing one stage does not approve later stages.
- Motion, homing, LED, camera trigger and scanner-sync approvals are independent.
- Approval must name the exact stage, hardware revision, channel or axis, allowed
  action, limits, stop conditions, evidence files and reviewer.
- Any unresolved blocker in `evidence/*.example.json`, board docs or subsystem
  docs keeps the affected stage closed.
- Z motion or Z homing requires a separate objective, slide and fixture collision
  review.
- A failed or ambiguous result returns the affected subsystem to docs-only status
  until evidence and approval are updated.

## Software-Only Proposal Records

`procedure_proposals` entries in evidence JSON files are planning records, not
test permissions. A Stage 0 or Stage 1 proposal may be checked in while
`approved=false`, `executed=false`, `hardware_access=software_only`,
`output_mode=none` and `evidence_refs=[]`.

Pending proposals must stay in that state until a human approval record exists
and the evidence refs for that approval are added. A pending proposal does not
change any live action gate and does not approve GPIO, serial, network,
firmware flashing, LED output, camera trigger output, motor enable, motion or
homing.

Current allowed proposal types:

| Proposal | Scope | Output authority |
|---|---|---|
| Stage 0 read-only inspection | Review checked-in docs, evidence files, blockers and validator results | none |
| Stage 1 dummy/no-load preflight | Prepare the required evidence checklist for a future dummy-load or no-load plan | none |

## Stage Order

| Stage | Gate | Depends on |
|---|---|---|
| 0 | No-motion/read-only | Current docs only |
| 1 | No-load output | Stage 0 approval and exact no-load measurement plan |
| 2 | Dummy-load LED | Stage 1 for the relevant LED gate and driver path |
| 3 | Low-current LED | Stage 2 for the same channel |
| 4 | Camera trigger | Stage 1 for trigger output and camera-interface evidence |
| 5 | One-axis low-speed | Stage 1 plus motion-driver and selected-axis evidence |
| 6 | Homing | Stage 5 for the selected axis plus homing-source evidence |
| 7 | Scanner-sync metadata | Approved metadata-only scope or the approved live stages it references |

## Stage 0: No-Motion/Read-Only

Purpose: collect and review static evidence without commanding hardware.

The software-only proposal form for this stage is read-only inspection. It may
describe what should be reviewed, but it remains unapproved and unexecuted until
human approval and evidence refs are recorded.

Preconditions:

- Scope is docs, checked-in evidence files, schematics, datasheets, photos or
  unpowered/disconnected inspection only.
- Exact hardware item is identified, or remains unknown.
- Reviewer approval explicitly says the activity is no-motion/read-only.

Allowed actions:

- Review repository docs and static evidence.
- Record unknowns, blockers and required evidence fields.
- Run offline validation scripts that only read checked-in files.

Stop conditions:

- Activity would require live controller access, GPIO, serial, network, motor,
  LED, camera trigger, firmware flashing or external integration.
- A value needed for the next stage is missing, conflicting or inferred.

Evidence to collect:

- Evidence refs reviewed, explicit unknowns and blockers, reviewer, date and
  permitted docs-only scope.

Approval required:

- One reviewer approval for no-motion/read-only scope. No later live stage is
  implied.

## Stage 1: No-Load Output

Purpose: verify boot/reset and commanded output behavior with no actuator,
camera input or LED load connected.

The software-only proposal form for this stage is dummy/no-load preflight. It
may prepare a checklist for a future measurement plan, but it must not connect a
dummy load, command a no-load output, toggle GPIO or access a live controller.
Actual Stage 1 output testing remains closed until the live-action gate is
approved with evidence.

Preconditions:

- Stage 0 is approved and complete for the target board and signal.
- Exact board revision, MCU, firmware path, voltage domain, output type, pin or
  connector mapping, common reference or isolation plan and test point are known.
- Instrument loading, voltage limits and pass/fail thresholds are recorded.
- Motors, LEDs, camera trigger input and other loads remain disconnected or
  physically unable to respond.

Allowed actions:

- Observe boot/reset state at the approved high-impedance test point.
- Command only the named output into the approved no-load measurement setup.
- Record waveform, polarity and timing at zero mechanical and optical load.

Stop conditions:

- Unexpected boot/reset state, voltage, polarity, pulse width, drive behavior or
  coupling to another output.
- Any load is connected, any motor driver can enable, or firmware/command path
  differs from the approved scope.

Evidence to collect:

- Setup diagram or photo reference, measured boot/reset state, waveform,
  instrument loading, measurement limits and pass/fail result.

Approval required:

- Stage-specific approval naming the exact output, firmware path, command and
  no-load measurement limits.

## Stage 2: Dummy-Load LED

Purpose: verify LED driver behavior without an actual LED installed.

Preconditions:

- Stage 1 has passed for the relevant LED gate and brightness/current-setpoint
  path.
- LED supply voltage, current budget, current-sense path, output type, gate
  polarity, boot/reset state and driver fault/default state are known.
- Dummy load, current limit, thermal rating, instrument limits and stop threshold
  are recorded.
- Actual red, green and white LEDs remain disconnected.

Allowed actions:

- Apply the approved dummy load or high-impedance measurement fixture.
- Request only the approved setpoint and gate pattern for the named channel.
- Measure gate signal, setpoint signal, current-sense voltage and supply rail.

Stop conditions:

- Current, voltage, temperature, rail droop, polarity or gate behavior differs
  from the approved expectation.
- Any actual LED is connected or any non-approved channel changes state.

Evidence to collect:

- Dummy-load value or instrument impedance, current-limit calculation, measured
  current-sense result, waveforms, rail measurement, command, duration, stop
  threshold and pass/fail result.

Approval required:

- Stage-specific approval for the exact LED channel and dummy-load limits.
- Actual LED connection or operational illumination requires separate approval.

## Stage 3: Low-Current LED

Purpose: perform the first actual LED connection at an explicitly approved low
current.

Preconditions:

- Stage 2 has passed for the same channel.
- Installed LED part or traceable identification, forward voltage, thermal path,
  maximum safe continuous and pulsed current, driver current limit, duty cycle or
  pulse width, duration and temperature limit are known.
- Approved first-current value is recorded. If it is not recorded, it remains
  unknown and this stage is closed.
- Eye/skin exposure controls and enclosure or shielding requirements are
  reviewed for the exact LED and current.

Allowed actions:

- Connect only the named LED channel.
- Request only the approved current, duty cycle or pulse width and duration.
- Observe current sense, rail voltage, brightness qualitatively and temperature.

Stop conditions:

- Current, voltage, brightness, temperature, polarity or timing differs from the
  approved expectation.
- Odor, visible damage, unexpected heating, unstable output or rail fault is
  observed.
- Any unapproved LED channel or camera trigger changes state.

Evidence to collect:

- LED identification, current limit and thermal evidence refs, requested setpoint
  and measured current, pulse width or duty cycle, duration, rail voltage,
  temperature observation and pass/fail result.

Approval required:

- Stage-specific approval for one LED channel, one current limit and one test
  duration.
- Higher current, other channels and scan illumination require new approval.

## Stage 4: Camera Trigger

Purpose: verify the camera trigger interface after no-load output behavior and
camera-side requirements are known.

Preconditions:

- Stage 1 has passed for the trigger output.
- Camera trigger voltage, active polarity, pulse-width limits, input protection,
  level shifting or isolation, boot/reset state and test point are known.
- First camera-connected test command, pulse timing and stop threshold are
  recorded.
- LED and motor actions are disabled unless separately approved.

Allowed actions:

- Connect only the approved trigger interface.
- Issue only the approved trigger pattern.
- Record trigger waveform at controller-side and camera-side test points.
- Record whether the camera reports an external-trigger event only if that local
  readout is part of the approved setup.

Stop conditions:

- Trigger voltage, polarity, pulse width, timing, boot/reset behavior or camera
  response differs from the approved expectation.
- Any LED output, motor output or unapproved integration becomes active.
- Camera model, cable, interface circuit or command path differs from approval.

Evidence to collect:

- Camera model or trigger-interface identity, controller-side and camera-side
  waveform captures, pulse timing, polarity, voltage and pass/fail result.

Approval required:

- Stage-specific approval for the exact camera trigger interface and pulse
  limits.
- Image-quality, exposure, diagnostic or clinical claims are out of scope.

## Stage 5: One-Axis Low-Speed

Purpose: verify controlled movement of one selected axis without homing.

Preconditions:

- Stage 1 has passed for the relevant enable, step, direction and safety outputs.
- Exact selected axis, step pin, direction pin, enable pin, driver model, current
  limit or Vref, thermal margin, travel envelope, direction convention, reduced
  speed, acceleration, move distance and timeout are known.
- Other axes are disabled or mechanically blocked from unintended motion.
- Emergency stop or power-off path has been reviewed without axis motion.
- Z is excluded unless separate collision review approves Z.

Allowed actions:

- Enable only the selected axis.
- Perform only the approved low-speed, reduced-current, bounded-distance move.
- Observe direction, travel, driver temperature and unexpected coupling.

Stop conditions:

- Unexpected direction, distance, sound, heat, missed steps, binding or driver
  fault.
- Any other axis moves or any LED/camera output changes state.
- Limit, timeout, travel envelope or emergency path is ambiguous.

Evidence to collect:

- Axis, driver settings, motion limits, commanded move, observed direction and
  distance, driver temperature observation, fault state, stop-path readiness and
  pass/fail result.

Approval required:

- Stage-specific approval naming one axis and prohibiting all other axes and
  homing.

## Stage 5a: Reviewed V1 Manual-Centered Bounded Non-Scan Bring-Up Without Homing

Purpose: allow the first scanner bring-up test without homing while preserving
a small manual-centered envelope and explicit stop conditions.

Safety status: hardware-affecting procedure definition only. This section does
not approve execution by itself.

This stage is not homing readiness, is not a scan workflow, and must not be
used to collect diagnostic, production, clinical, tiling, stitching or
performance evidence. It exists only to review a bounded live bring-up procedure
for V1 hardware when the operator manually centers the field before motion.

Default scope:

- X/Y bounded motion from a manually established local center.
- Optional Z focus-search motion only when a separate Z collision review and
  focus-search envelope are approved.
- No homing, no hard-stop approach, no scan recipe execution, no camera capture
  workflow, no scanner-sync hardware-output workflow and no hardware outputs
  except the exact motion scope named by the approval record.
- LED, camera trigger, scanner-sync diagnostic GPIO, spare GPIO and any other
  non-motion output remain off or physically disconnected until the approval
  record explicitly names that output, its electrical limits and its evidence
  gate and the operator confirms the approved state at start-of-run.

Preconditions:

- Stage 1 has passed for the selected X/Y motion outputs and any output that
  can affect LED or camera-trigger state.
- A reviewed approval record names `V1 manual-centered bounded non-scan
  bring-up`, the operator, reviewer, date, exact board/profile, allowed axes,
  limits, stop conditions, evidence refs and rollback or recovery expectation.
- The operator approves start-of-run only after verifying the live setup still
  matches the reviewed record; operator approval does not expand the reviewed
  scope.
- The operator manually centers the camera/stage on the intended field before
  the test and records the manual center method. This local center is not
  machine zero, slide origin, ROI origin or homing evidence.
- X/Y travel envelope is limited to `+/-10 mm` from the manual center.
- Initial X/Y speed is `0.5-1 mm/s`; initial X/Y acceleration is
  `5-10 mm/s^2`.
- Z starts from manual focus setup. Any Z movement is limited to the separately
  approved autofocus search range and is not treated as homing.
- Homing commands and hard-stop approaches are disabled and prohibited.
- Scan commands, scan recipes, tiling workflows, autofocus scans, automated
  acquisition workflows and any command that can derive motion from a scan ROI
  are disabled and prohibited.
- Hardware outputs are default-deny. LED gate/current outputs, Raspberry Pi HQ
  Camera XVS trigger output, camera exposure trigger, scanner-sync
  hardware-output mode, diagnostic GPIO and spare GPIO must be disabled,
  disconnected or outside the command path unless the approval explicitly
  includes that exact output and the operator approves the start-of-run state.
- If the Raspberry Pi HQ Camera XVS path is present, the approval records
  whether HQ XVS is disconnected, dummy-loaded or connected. A connected HQ XVS
  path requires separate camera-trigger approval and camera-side waveform,
  polarity, pulse-width and boot/reset inactive-state evidence.
- LED current approval is separate from LED timing/gate approval. Constant
  white illumination or any nonzero LED current setpoint requires reviewed
  current-limit, current-sense, rail-budget, thermal and live-test approval for
  the exact channel. A timing GPIO or gate approval alone does not approve LED
  current.
- Scanner-sync metadata review, if present, remains metadata-only with
  `hardware_outputs_enabled=false` unless Stage 7 and the referenced live output
  stages are separately approved. `FRAME_EVENT` records are identity metadata,
  not permission to trigger a camera, strobe LEDs or claim captured images.
- Fluidd emergency stop and physical power removal are both available before
  motion begins.

Operator preconditions:

- The operator has direct line of sight to the stage, objective, slide area and
  cables during the whole run.
- The operator can reach the physical power-removal path without crossing the
  moving stage envelope.
- The stage has clear `+/-10 mm` X/Y travel from the manual center; cables,
  fixtures, slide holder and objective clearance are checked before enable.
- The operator confirms other axes are disabled or otherwise prevented from
  unintended motion, and confirms Z is excluded unless the approval names the
  Z focus-search envelope.
- The operator confirms the live controller path, command source and emergency
  stop path match the approval exactly. If any path differs, the run remains
  docs-only.

Allowed actions:

- Enable only the approved X/Y motion outputs required for the selected moves.
- Perform only approved X/Y bounded moves inside the manual-centered envelope,
  using the named reduced speed, acceleration, current and timeout limits.
- Perform only approved small Z focus-search moves after manual focus setup.
- Use constant white illumination only if the LED current live-test approval
  explicitly includes the exact channel, setpoint/current limit and monitoring
  evidence.
- Observe direction, distance, coupling, heat, noise, cable movement, objective
  clearance and stop-path readiness after each move.

Stop conditions:

- Any homing command, hard-stop approach, unapproved Z move or travel outside
  the manual-centered envelope occurs.
- Any scan workflow, scan recipe, tiling/acquisition workflow, autofocus scan,
  camera capture workflow or scanner-sync hardware-output workflow is invoked.
- Any LED, HQ XVS/camera trigger, diagnostic GPIO, spare GPIO or other hardware
  output changes state outside the exact approval scope.
- Any nonzero LED current is requested without the separate LED current gate
  approval, or any LED current-sense/current-limit evidence is missing or
  ambiguous.
- Any `FRAME_EVENT` stream is treated as captured-image evidence while
  `hardware_outputs_enabled=false` or while camera trigger approval is absent.
- Unexpected X/Y/Z direction, coupling, noise, heat, missed steps or stall.
- Fluidd emergency stop is unavailable or does not respond as expected.
- The operator loses direct sight of the stage, objective, cables or stop path.
- Approval, command source, board/profile, axis mapping, current limit,
  envelope, speed, acceleration, timeout, lighting scope or camera-trigger
  scope differs from the reviewed record.

Evidence to collect:

- Approval record ID, reviewer, operator, date/time, board/profile, exact
  command source and recovery expectation.
- Manual center setup, photos or notes sufficient to identify the local center,
  X/Y `+/-10 mm` soft envelope, optional Z focus-search envelope and Z collision
  review when Z is in scope.
- Verified X/Y step/direction/enable mappings, driver current limit or Vref,
  reduced speed, acceleration, timeout and other-axis-disabled state.
- Commanded moves, observed direction and distance, coupling/noise/heat/stall
  observations, driver fault state and stop-path readiness.
- Lighting scope and measured state: LED outputs off/disconnected, or separate
  LED current approval with current-limit/current-sense/rail-budget refs.
- Camera-trigger scope and measured state: HQ XVS/camera trigger
  off/disconnected/dummy-loaded/connected as approved, with camera-trigger
  evidence refs when connected.
- Scanner-sync state if present: metadata-only or approved hardware-output
  scope, `hardware_outputs_enabled` value, and any `FRAME_EVENT` artifact marked
  as identity metadata only unless camera capture is separately approved.
- Stop conditions encountered, pass/fail result and explicit unknowns or
  blockers returned to docs-only status.

Approval required:

- Stage-specific approval naming `V1 manual-centered bounded non-scan
  bring-up`, X/Y `+/-10 mm`, reduced current/speed/acceleration/timeout limits,
  optional Z focus-search range, disabled homing commands, prohibited scan
  workflows, lighting scope, camera-trigger/HQ XVS scope, scanner-sync output
  scope, stop path and evidence refs.
- Approval for this stage does not approve homing, normal scan workflows,
  camera capture, HQ XVS trigger connection, LED current, LED timing/gate
  output, scanner-sync hardware outputs or firmware flashing unless those items
  are separately named by their own gates.

References:

- Raspberry Pi HQ Camera XVS trigger gate:
  [../electronics/camera-trigger/README.md](../electronics/camera-trigger/README.md)
- V1 board safe-test assumptions:
  [../boards/mks-robin-mini-v2-scanner/safe-test-plan.md](../boards/mks-robin-mini-v2-scanner/safe-test-plan.md)
- LED current and gate separation:
  [../electronics/led-driver/rev-a5-arduino-pwm-brightness-controller.md](../electronics/led-driver/rev-a5-arduino-pwm-brightness-controller.md)
- Firmware `FRAME_EVENT` identity and metadata-only behavior:
  [controller/docs/scheduling/frame-event-emission.md](https://github.com/FAST-OFM/controller/blob/v0.3.0-prototype.1/docs/scheduling/frame-event-emission.md)
- Scanner-sync live protocol hardware-output separation:
  [controller/docs/klipper/klipper-scanner-sync-live-protocol-contract.md](https://github.com/FAST-OFM/controller/blob/v0.3.0-prototype.1/docs/klipper/klipper-scanner-sync-live-protocol-contract.md)

## Stage 6: Homing

Purpose: verify homing for one selected axis only.

Preconditions:

- Stage 5 has passed for the same axis.
- Homing source, endstop or sensor input, active polarity, pull-up or pull-down
  behavior, debounce/noise plan, timeout, reduced speed/current, backoff distance
  and false-positive/false-negative risks are known.
- Homing source can be observed before relying on a hard stop as proof of
  detection.
- Z homing has separate objective, slide and fixture collision approval.

Allowed actions:

- Home only the named axis using the approved source and limits.
- Observe input state transitions, timeout behavior and backoff.
- Record repeatability only within the approved trial count.

Stop conditions:

- Input state does not match expected polarity before motion.
- Axis approaches an unprotected hard stop, exceeds timeout, moves in the wrong
  direction, fails to back off or heats unexpectedly.
- Any unapproved axis, LED or camera trigger changes state.

Evidence to collect:

- Homing source identity, input behavior, command, speed/current limits, timeout,
  backoff, trial count, final state, repeatability observation, pass/fail result
  and separate Z collision review when applicable.

Approval required:

- Stage-specific approval naming one axis, homing source, limits and trial count.
- Homing approval for one axis does not approve scan workflows.

## Stage 7: Scanner-Sync Metadata

Purpose: verify that generated metadata describes approved hardware events
without making unsupported timing or clinical claims.

Preconditions:

- Metadata schema, frame/event ID source, position source, units, timestamp or
  counter source, LED channel fields, trigger fields, axis fields and unknown
  markers are documented.
- If metadata references live trigger, LED, motion or homing events, those stages
  are separately approved and passed for the exact referenced scope.
- Simulator-only metadata is clearly marked simulator or dry-run and does not
  imply live hardware validation.

Allowed actions:

- Generate or review scanner-sync metadata for approved simulator/dry-run events
  or approved live-stage events.
- Check that frame IDs, position metadata, LED channel labels, trigger labels and
  unknown fields match the approved evidence.
- Record metadata files and validation output.

Stop conditions:

- Metadata fills an unknown value, drops an uncertainty marker, changes units
  without evidence or implies unapproved hardware action.
- Metadata claims clinical, diagnostic, regulatory, safety-certified or
  performance-validated status.
- Metadata uses Raspberry Pi userspace time as coordinate truth for acquisition
  events instead of the approved position-indexed source.

Evidence to collect:

- Metadata artifact path and schema/version, source stage approvals, validation
  output, field-level review of unknowns and explicit R&D-only status.

Approval required:

- Metadata-only approval for simulator/dry-run artifacts.
- Separate approval for any metadata generated from live trigger, LED, motion or
  homing tests.

## Current Repository Status

Checked-in evidence currently leaves live hardware gates blocked by unknowns.
Use this ladder to plan and review future evidence. Do not treat it as
permission to perform any stage.
