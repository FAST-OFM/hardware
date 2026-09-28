# LED Rev A: Simple Controller-Driven Channels

## Purpose

Rev A is for fast R&D using available LEDs. It is not the final high-speed strobe design.

## Allowed implementation

Small LED channel:

```text
verified controller-board LED rail
  → current limiting resistor
  → LED
  → MOSFET / transistor / board MOSFET output
  → GND

MCU GPIO
  → gate/base/enable input
```

The GPIO is a control signal. It must not directly source or sink illumination LED current.

## Required measurements before use

- Controller-board rail voltage.
- Available current budget of the rail.
- LED forward voltage at intended current.
- Series resistor value.
- Actual LED current.
- MOSFET/output polarity.
- Default state during boot/reset.
- Whether LED remains off during firmware crash/reset.

## Initial current policy

Unknown LEDs start at zero/off. Do not request any nonzero LED current until
the LED part, forward voltage, thermal path, rail budget, current limit,
output type and boot/reset default state are recorded and reviewed.

Suggested discovery ladder after the required measurements and approvals exist:

```text
1 mA diagnostic check
5 mA visibility check
10 mA first image check
20 mA autofocus geometry check
30–50 mA only if LED and thermal limits are known
```

Do not use high-current white illumination from the controller board unless the
rail and thermal path are explicitly verified.

## Why this is acceptable

The first objective is not maximum scan speed. The first objective is to validate:

- illumination geometry;
- red/green oblique autofocus mechanism;
- raw Bayer processing;
- static focus calibration;
- frame metadata and slow acquisition.

Slow scan modes can compensate for low LED brightness.

## Current 20x AF LEDs

The currently installed red and green AF LEDs are 100 mA-class devices in the
`20x` objective geometry. They are not the final high-power LED choice.

Current geometry:

- lateral offset from optical center: 10 mm;
- distance from tissue plane: 35 mm;
- placement angle: 16 degrees.

The `40x` objective must use a separate LED pair with its own angle, current
limits and calibration records.

## Upgrade path

Later revisions replace the physical channel with:

```text
external constant-current driver
or
external fast strobe driver
```

The logical firmware pattern remains the same.
