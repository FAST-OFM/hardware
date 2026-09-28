# LED Driver / LED Interface

## Current decision

Revision A may use the LEDs available in the lab and simple controller-driven
LED channels after LED part, rail budget, current limit, output type and
boot/reset evidence are recorded. Dedicated high-current strobe drivers are a
future upgrade, not a Revision A requirement.

## Channels

- `WHITE_BF`: white brightfield.
- `AF_RED`: red oblique autofocus.
- `AF_GREEN`: green oblique autofocus.

## Revision A

For small LEDs:

```text
verified controller-board low-voltage rail
  → current limiting resistor
  → LED
  → MOSFET / transistor / board MOSFET output
  → GND
```

The MCU controls timing through GPIO, but GPIO pins do not directly carry illumination LED current.

Revision A supports slow modes:

- step-stop capture;
- micro-stop capture;
- slow segmented scan after measurement.

## Future revisions

Future hardware may add:

- external constant-current drivers;
- fast strobe drivers;
- current monitor;
- thermal monitor;
- hardware duty protection;
- hardware LED disable.

Revision A.5 may add an Arduino-compatible USB brightness controller. In that
variant, Arduino PWM sets slow brightness/current references, while the MKS
controller still owns LED gate timing and camera/frame synchronization. See
`rev-a5-arduino-pwm-brightness-controller.md`.

## Open questions

- Exact LED part numbers currently available.
- Controller-board rail current budget.
- Safe current per LED.
- Required exposure time for useful BF and AF frames.
- Whether small LEDs provide enough SNR for red/green autofocus.
- When a dedicated driver is justified by measured photon budget.
