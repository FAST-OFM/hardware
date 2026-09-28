# MKS Robin Mini V2 Scanner Discovery Log

Status: docs-only log assembled from checked-in evidence.

No firmware flashing, GPIO toggling, motor motion, camera triggering, LED
driving, serial control, network control, probing or hardware test was performed
for this profile.

## 2026-07-02 Profile Creation

Created bounded scanner board profile under
`boards/mks-robin-mini-v2-scanner/`.

Sources reviewed:

- `AGENTS.md`
- `README.md`
- `docs/controller-discovery/controller-board-discovery.md`
- `docs/controller-discovery/board-porting-guide.md`
- `docs/controller-discovery/controller-discovery-status.md`
- `electronics/led-driver/rev-a5-arduino-pwm-brightness-controller.md`
- `electronics/camera-trigger/README.md`
- `evidence/rev-a5-evidence-status.example.json`
- `mechanics/homing/README.md`
- `mechanics/homing/pico-sensorless-homing-feasibility.md`

## Extracted Evidence

- Board baseline is documented as MKS Robin Mini V2.0 with PCB code
  `M-M-B-A-00526`.
- MCU evidence is documented as STM32F103-family from current Klipper
  deployment.
- Stepper drivers are documented as A4988.
- Current documented mechanics use NEMA 11 motors.
- X/Y screw pitch is documented as 2 mm per revolution.
- Z screw pitch is documented as 0.5 mm per revolution.
- Current MKS setup has no verified homing implementation.
- Current A4988 setup has no documented sensorless-homing feedback path.

## Candidate Signal Evidence

The Rev A5 LED/trigger docs and evidence-status JSON document these current
assignments:

- `PD6` / `E0_STEP`: HQ Camera XVS sync output, 3.3 V at MKS and requiring
  the approved 3.3 V-to-1.8 V level shifter before HQ XVS.
- `PA9` / `WiFi TXD1`: green LED gate, positive polarity.
- `PA10` / `WiFi RXD1`: red LED gate, positive polarity.
- `PB13` / `TC1 SCK`: white LED gate, positive polarity.

The controller discovery status describes these as prior observations and warns
that they must not be copied into a generic MKS/Kingroon board profile without
review. This profile keeps them scoped to the current scanner and marks them as
candidate, not verified.

## Explicit Non-Evidence

No checked-in source was found in this repo that verifies:

- exact MCU part number;
- firmware flashing/debug procedure for the exact target;
- X/Y/Z step, direction and enable pins;
- endstop pins or working homing inputs;
- pin voltage levels and output drive limits;
- reset/default states for candidate output pins;
- loaded LED gate behavior;
- camera trigger electrical compatibility;
- rail voltage/current budgets;
- stepper current limits or thermal margins.

## 2026-07-02 HQ XVS Rename

Live Pi5 config was renamed away from legacy generic camera-trigger naming:

- active Klipper output: `hq_xvs_sync`;
- active macros: `HQ_XVS_HIGH`, `HQ_XVS_LOW`, `HQ_XVS_PULSE`,
  `HQ_XVS_TEST_TRAIN`;
- old names `e_step_trigger`, `ARS_TRIGGER_*` and
  `SCANNER_E_STEP_TRIGGER*` are legacy names and should not be used for new
  work.

After the rename, Klipper loads the host config but the MKS currently does not
answer `identify_response`. Keep this as a connectivity/firmware-mode gate
before flashing or hardware tests.

## Next Docs-Only Actions

- Link any future reviewed worksheet or bench note into this directory.
- Keep unknown electrical and motion fields explicit until evidence is added.
- Raise the profile state only after reviewed evidence satisfies the board
  discovery restrictions.
