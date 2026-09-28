# LED Rev A.5: Arduino PWM Brightness Controller

## Purpose

Revision A.5 adds adjustable LED brightness while preserving the MKS controller
as the timing source.

The Arduino controls LED current setpoints. It does not control frame timing.

## System Role Split

```text
Raspberry Pi
  -> USB serial brightness commands
  -> Arduino Nano-compatible controller
  -> PWM_RED / PWM_GREEN / PWM_WHITE
  -> low-pass filters / buffers
  -> LED current setpoints

MKS Robin Mini V2.0 timing MCU
  -> RED/GREEN/WHITE gate signals
  -> camera trigger
  -> FRAME_EVENT metadata
```

Current MKS signal assignment:

```text
PD6 / E0_STEP     -> camera/sync trigger
PA9 / WiFi TXD1   -> GREEN LED gate, positive polarity
PA10 / WiFi RXD1  -> RED LED gate, positive polarity
PB13 / TC1 SCK    -> WHITE LED gate, positive polarity
```

These assignments identify intended controller signal names only. They do not
prove LED connector wiring, output type, drive strength, boot/reset state, rail
voltage, rail current budget, LED part number, LED current limit, or safe output
state.

## One-Channel Electrical Model

```text
brightness path:

Arduino PWM
  -> R_FILTER
  -> C_FILTER to GND
  -> optional op-amp buffer
  -> current-setpoint input

timing path:

MKS LED_GATE
  -> gate/enable input
  -> current sink enabled only during requested LED window

power path:

+V_LED
  -> LED
  -> current-regulated sink
  -> R_SENSE
  -> GND
```

The LED current path must have a hardware current limit. Arduino firmware is
not a safety limit.

## PWM Filter Starting Point

Start conservatively:

```text
R_FILTER = 10 kOhm
C_FILTER = 1 uF
tau = 10 ms
```

This is intended for slow brightness setpoints, not per-frame modulation.

If ripple is too high, increase capacitance or PWM frequency. If settling is
too slow, reduce the time constant after measurement.

The current Arduino Nano firmware uses high-frequency PWM:

```text
RED   = D9  / Timer1 OC1A / ~62.5 kHz
GREEN = D10 / Timer1 OC1B / ~62.5 kHz
WHITE = D3  / Timer2 OC2B / ~62.5 kHz
```

Red and green share Timer1, so their PWM frequencies match.

Current feedback mapping:

```text
RED   PWM D9  -> sense A0 -> 12 ohm sense resistor
GREEN PWM D10 -> sense A1 -> 12 ohm sense resistor
WHITE PWM D3  -> sense A2 -> 12 ohm sense resistor
```

The red and green LEDs installed in the current bench setup are higher-power
lab LEDs than the earlier small placeholders. Their exact part numbers,
forward voltages, maximum safe current and thermal limits remain unknown until
measured or verified from datasheets.

## Current-Setpoint Policy

Unknown LED channels start at zero current.

Brightness setpoints must be limited by hardware and configuration:

```text
setpoint_min = 0
setpoint_max = measured_safe_value
boot_default = 0
fault_default = 0
```

Do not connect LEDs until:

- LED part or safe current is known;
- series/current-sense resistor values are reviewed;
- rail voltage is measured;
- supply current budget is known;
- MKS gate default state is verified;
- Arduino boot/reset output state is verified.
- LED gate output type is known for the exact circuit;
- LED driver fault/default current behavior is known;
- dummy-load or high-impedance driver testing is approved and recorded;
- first low-current LED test current, duty/pulse width, duration, temperature
  limit and stop criteria are approved and recorded.

## Trigger/LED No-Guess Evidence Gate

The evidence map for this Rev A.5 path is
`evidence/rev-a5-evidence-status.example.json`. Keep unknowns explicit in that
file until reviewed evidence exists. Do not guess:

- controller pin behavior beyond the checked-in signal assignment;
- LED white, red or green connector wiring;
- LED rail voltage or current budget;
- LED part numbers, forward voltage, thermal path or current limits;
- output type, drive strength, source/sink behavior or protection;
- boot/reset, fault or default output states;
- camera trigger electrical requirements or output behavior.

Live LED work remains prohibited by the no-guess gate until the required
evidence fields are recorded, including dummy-load/current-sense results before
actual LEDs and a separately approved first low-current LED test.

## Ground and Level Rules

- Raspberry Pi, Arduino, MKS controller and LED driver need a reviewed common
  reference or isolation plan.
- If Arduino runs at 5 V, do not connect 5 V logic directly into 3.3 V-only
  inputs.
- Arduino PWM output must not directly drive LED current.
- MKS GPIO must not directly drive LED current.

## Required Test Points

Per channel:

- Arduino PWM before filter;
- filtered VREF/current setpoint;
- MKS gate signal;
- LED current sense voltage;
- LED supply rail.

## Bring-Up Order

1. Arduino connected over USB only; no LED driver connected.
2. Verify serial protocol and boot default setpoints.
3. Measure PWM duty and filtered voltage into high impedance.
4. Connect dummy current-sink input or resistor load, no LED.
5. Verify MKS gate disables current even when Arduino setpoint is nonzero.
6. Connect low-current LED with conservative current limit.
7. Record current, brightness, temperature and image exposure.

## Current Lab Status

As of the current bring-up:

```text
Arduino board: Nano-compatible ATmega328P
USB bridge: CH340
Raspberry Pi runtime port: /dev/serial/by-path/platform-xhci-hcd.1-usb-0:1:1.0-port0
Bootloader: old Nano bootloader, upload at 57600 baud
Runtime serial: 115200 8N1
Firmware flashed: yes
Serial protocol verified: yes
Firmware config version: 5
Sense resistors: RED=12 ohm GREEN=12 ohm WHITE=12 ohm
Saved EEPROM output state after calibration: RED=0 GREEN=0 WHITE=0
Saved EEPROM calibration: RED_MIN_PWM=71 GREEN_MIN_PWM=82 WHITE_MIN_PWM=88
Saved EEPROM max PWM: RED_MAX_PWM=255 GREEN_MAX_PWM=255 WHITE_MAX_PWM=255
Current bench test PWM setpoint policy: use raw PWM=255 for each tested channel
```

The raw `255` bench setpoint is a temporary test convention for the current
external driver/current-limit setup. It is not a general safe-current claim and
must not be reused for a different LED, driver, supply, thermal path or optical
assembly without a fresh current and temperature check.

Latest measured current table with the current 12 ohm sense resistors and the
current bench circuit:

```text
GREEN: PWM 255 -> 61.50 mA
RED:   PWM 255 -> 74.50 mA
WHITE: PWM 255 -> 62.08 mA
```

During paired red+green gate testing with raw PWM 255 on the current bench
circuit, white feedback reported about 4.42 mA while the white gate was
commanded off. The paired red+green blink was not visually synchronous when
driven through host-issued Klipper `SET_PIN` commands. Setting the white PWM
channel to 0 did not change the white feedback reading, and all feedback
channels returned to 0 mA after red+green gates were disabled. Treat this as a
bench-circuit coupling, common-reference, ADC crosstalk or driver-isolation
item to investigate before relying on white-off purity during autofocus windows.
For autofocus testing, red and green gates should be enabled before the camera
trigger and held through a configured settle interval; do not assume host-issued
`SET_PIN` commands provide microsecond-synchronous red/green edges.

Before testing actual LEDs, record:

- filtered VREF for red, green and white;
- LED driver input polarity;
- LED current-sense voltage;
- LED supply rail voltage;
- series/current-sense resistor values;
- LED case or board temperature during the first low-current test.

## Not Allowed

- Arduino USB timing for frame identity.
- Arduino USB timing for camera trigger.
- Arduino USB timing for LED strobe window.
- LED current controlled only by software with no hardware current limit.
- Unknown LED current or rail budget treated as safe.
