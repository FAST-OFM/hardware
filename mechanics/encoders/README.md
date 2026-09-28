# Future Linear Encoder Integration

## Goal

Reserve mechanical/electrical path for future X/Y linear encoders.

## Design considerations

- Location of scale relative to motion axis.
- Readhead mounting stiffness.
- Cable routing and shielding.
- Index/reference signal.
- Interface electronics.
- Encoder-to-image calibration.

## Offline readiness evidence

The current non-live readiness snapshot is:

- `evidence/encoder-readiness-evidence-status.example.json`

It is a documentation/data artifact only. It records encoder-readiness
unknowns and blockers without selecting encoder parts, assigning electrical
levels, choosing controller inputs, or measuring hardware behavior.

Hardware-specific values remain unknown until supporting evidence is added and
the relevant entry is removed from `required_unknowns`.

## Development stages

1. Mechanical reservation.
2. Read encoder in diagnostics.
3. Record encoder counts in frame metadata.
4. Use encoder counts for QA.
5. Generate trigger from encoder counts.
