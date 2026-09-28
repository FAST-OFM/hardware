# Hardware Safety Guardrails

## LEDs

- Use current-limited drivers, not GPIO direct drive.
- Document max current, pulse width, duty cycle and thermal path.
- Default off on boot/reset.
- Add test points for LED current waveform.

## Camera trigger

- Verify camera trigger voltage and polarity before connecting.
- Use level shifting or resistor divider where required.
- Add test point for trigger signal.

## Motors and homing

- Add limit/homing switches before high-speed scans.
- Verify direction and soft limits at reduced current/speed.
- Z axis must have safe motion rules to avoid objective/slide collision.

## Encoders

- Plan encoder mounts, cable routing and signal inputs before mechanical redesign.
- Keep encoder signals away from noisy motor/LED power lines when possible.
