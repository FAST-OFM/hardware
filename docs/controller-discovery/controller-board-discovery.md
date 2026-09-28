# Controller Board Discovery for Firmware Work

Firmware work must not begin from guessed board definitions.

## Board profile states

```text
placeholder
  board exists as a named target but no pins are trusted

discovered
  MCU and flashing method are known

pinmap_candidate
  candidate pins exist but are not electrically verified

pinmap_verified
  pins and voltage levels are verified enough for safe dry-run firmware

hardware_tested
  safe no-motion and one-axis low-speed tests passed
```

## Required board profile files

```text
boards/<board>/board.md
boards/<board>/pins.yaml
boards/<board>/discovery-log.md
boards/<board>/safe-test-plan.md
```

## Firmware restrictions

Until `pinmap_verified`:

- do not emit step pulses on real hardware;
- do not enable motor drivers;
- do not drive LED outputs;
- do not connect camera trigger output to camera;
- simulator-only code is allowed.

## Discovery output

Copy or link the filled controller worksheet from scanner-docs into the board directory once reviewed.
