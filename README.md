<p align="center">
  <a href="https://github.com/FAST-OFM">
    <img src="https://github.com/FAST-OFM.png?size=200" alt="Fast OFM logo" width="132">
  </a>
</p>

<h1 align="center">Fast OFM Hardware</h1>

<p align="center">
  <strong>Motion, illumination, optical interfaces and safety evidence</strong>
</p>

<p align="center">
  <a href="https://github.com/FAST-OFM/fast-ofm">Project index</a> ·
  <a href="https://github.com/FAST-OFM/openflexure-wsi">WSI integration</a> ·
  <a href="https://github.com/FAST-OFM/controller">Controller</a> ·
  <a href="https://github.com/FAST-OFM/hardware">Hardware</a>
</p>

<p align="center">
  <sub>Research prototype · Verify electrical limits before reproducing hardware</sub>
</p>

Hardware documentation for the electronics, optics and mechanics of Alexander
Fridman's Fast OFM research prototype.

Start with [STATUS.md](STATUS.md), [DISCLAIMER.md](DISCLAIMER.md) and the
machine-specific observed configuration in
[`boards/mks-robin-mini-v2-scanner/observed-prototype-pins.yaml`](boards/mks-robin-mini-v2-scanner/observed-prototype-pins.yaml).
The adjacent `pins.yaml` is an older docs-only candidate profile and is not the
configuration observed in the accepted scan.

Original hardware documentation is source-available under CC-BY-NC-SA-4.0,
and software utilities use PolyForm-Noncommercial-1.0.0. Commercial use is not
granted. See [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md).

## Areas

- LED strobe driver.
- Camera trigger level shifting.
- LED mechanical mount and illumination geometry.
- Homing switches.
- Future linear encoder integration.
- Stage and slide holder mechanics.

## Evidence status

- `evidence/prototype-checkpoint-2026-09-09.md` records the exact bounded
  hardware/runtime state used for the `v0.1.0-prototype.1` checkpoint without
  promoting it to production or clinical readiness.
- `evidence/evidence-status.schema.json` defines the offline evidence-status JSON shape.
- `evidence/rev-a5-evidence-status.example.json` records current Rev A5 known signal assignments and explicit unknowns for current limits, rail limits, unverified mappings, output states and approvals.
- `evidence/pi-startup-hardware-evidence-status.example.json` records prerequisites and no-live-action gates for lifting the Pi startup `hardware_evidence_unknown` blocker.
- `evidence/controller-board-discovery-evidence-status.example.json` records the
  current MKS controller profile state, candidate output assignments and
  unknowns that block pinmap verification and live hardware action.
- `scripts/validate_evidence_status.py` validates evidence-status JSON files without accessing hardware.
- `scripts/validate_evidence_status.py --emit-telemetry-jsonl` validates
  checked-in evidence and emits software-only telemetry-style JSONL records
  such as `evidence_ledger_written` and `safety_gate_blocked`; emitted records
  keep hardware outputs disabled and preserve unknown, blocker and gate IDs.
- `docs/hardware-gated-test-procedure-ladder.md` defines the staged
  no-motion, no-load, LED, camera, motion, homing and scanner-sync metadata
  gates. It is a procedure definition only, not hardware approval.
- Checked-in live gate records must keep `approved=false` and `executed=false`
  while any blocker remains unresolved.

## Controller Discovery

Controller and board discovery artifacts live under
`docs/controller-discovery/`. These files record board-porting steps, current
MKS/Kingroon discovery status and unknowns. Unknown pins, voltage levels,
current budgets and reset states must remain unknown until measured.

Pi startup hardware prerequisites are documented in
`docs/pi-startup-hardware-evidence-prerequisites.md`. They do not approve live
controller access, GPIO, motor, LED or camera action.
