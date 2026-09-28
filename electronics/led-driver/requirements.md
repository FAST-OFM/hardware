# LED Driver Requirements

## Channels

- WHITE brightfield.
- RED oblique autofocus.
- GREEN oblique autofocus.
- Optional future BLUE/NIR channels.

## Revision A electrical requirements

- Available LEDs may be used.
- Small LEDs may be powered from a verified controller-board low-voltage rail.
- MCU GPIO pins are control signals only.
- Current limiting is mandatory per LED channel.
- LED channels default OFF during boot/reset.
- Test points should expose control signals and current measurement points.
- Unknown LED and rail limits remain unknown until measured.

## Revision A scan assumptions

- Long exposure is acceptable.
- Slow scan mode is acceptable.
- Microsecond strobe is not assumed.

## Future driver requirements

- TTL/logic enable per channel from MCU.
- Constant-current or fast current-regulated drive per channel.
- Rise/fall time suitable for short strobe pulses, if fast scan requires it.
- Current monitor per channel.
- Thermal monitoring for high-power LEDs.
- Hardware disable / interlock for future high-power illumination.

## Revision A.5 Arduino brightness requirements

- Arduino-compatible USB controller may set brightness/current references.
- Arduino PWM must be filtered and treated as a slow setpoint, not a frame
  timing signal.
- MKS controller remains the LED gate timing source.
- Arduino boot/reset/fault state must force LED current setpoints to zero or a
  verified safe minimum.
- Hardware current limiting is mandatory even if Arduino firmware clamps
  setpoints.
- Test points must expose PWM, filtered VREF, LED gate and LED current sense.

## Unknowns to measure

- required pulse width at target brightness;
- maximum safe pulse current;
- controller-board rail current budget;
- thermal behavior at scan duty cycle;
- electrical noise coupled into camera/motor system;
- whether small available LEDs are sufficient for slow AF calibration.
