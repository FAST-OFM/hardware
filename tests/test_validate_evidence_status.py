from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_evidence_status import (
    TelemetryProjectionError,
    ValidationError,
    main,
    project_evidence_to_telemetry_records,
    validate_document,
    validate_file,
    validate_telemetry_records,
)


EXAMPLE_PATH = REPO_ROOT / "evidence" / "rev-a5-evidence-status.example.json"
ENCODER_EXAMPLE_PATH = REPO_ROOT / "evidence" / "encoder-readiness-evidence-status.example.json"
PI_STARTUP_EXAMPLE_PATH = REPO_ROOT / "evidence" / "pi-startup-hardware-evidence-status.example.json"
HOMING_EXAMPLE_PATH = REPO_ROOT / "evidence" / "homing-readiness-evidence-status.example.json"
CONTROLLER_EXAMPLE_PATH = (
    REPO_ROOT / "evidence" / "controller-board-discovery-evidence-status.example.json"
)
EXAMPLE_PATHS = sorted((REPO_ROOT / "evidence").glob("*.example.json"))


@pytest.fixture()
def example_document() -> dict:
    with EXAMPLE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture()
def encoder_document() -> dict:
    with ENCODER_EXAMPLE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture()
def pi_startup_document() -> dict:
    with PI_STARTUP_EXAMPLE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture()
def homing_document() -> dict:
    with HOMING_EXAMPLE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture()
def controller_document() -> dict:
    with CONTROLLER_EXAMPLE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def entry_by_id(document: dict, entry_id: str) -> dict:
    return next(entry for entry in document["entries"] if entry["id"] == entry_id)


def proposal_by_id(document: dict, proposal_id: str) -> dict:
    return next(
        proposal
        for proposal in document["procedure_proposals"]
        if proposal["id"] == proposal_id
    )


@pytest.mark.parametrize("path", EXAMPLE_PATHS)
def test_example_files_validate(path: Path) -> None:
    validate_file(path)


@pytest.mark.parametrize(
    "entry_id",
    [
        "led_current_limit.af_red",
        "rail_limit.led_supply_current_budget",
        "pin_mapping.driver.af_red_led_connector",
        "output_type.camera_trigger",
        "output_type.af_red_led_gate",
        "output_state.mks_led_gates_at_boot",
        "output_state.camera_trigger_at_boot",
        "camera_trigger_behavior.electrical_compatibility",
        "test_prerequisite.dummy_load_led_driver",
        "approval.actual_led_connection",
        "approval.camera_trigger_connection",
    ],
)
def test_required_unknowns_must_remain_explicit_unknowns(
    example_document: dict, entry_id: str
) -> None:
    document = copy.deepcopy(example_document)
    entry = entry_by_id(document, entry_id)
    entry["status"] = "known"
    entry["value"] = {"unsafe_guess": True}
    entry["evidence_refs"] = ["bench-notes.md"]
    entry.pop("unknown_reason", None)

    with pytest.raises(ValidationError, match="must remain status 'unknown'"):
        validate_document(document)


def test_unknown_entry_must_not_carry_value(example_document: dict) -> None:
    document = copy.deepcopy(example_document)
    entry = entry_by_id(document, "led_current_limit.af_green")
    entry["value"] = {"max_current_ma": 20}

    with pytest.raises(ValidationError, match="unknown entries must not carry values"):
        validate_document(document)


def test_known_entries_reject_unknown_placeholders(example_document: dict) -> None:
    document = copy.deepcopy(example_document)
    entry = entry_by_id(document, "pin_mapping.mks.pa9.green_gate")
    entry["value"]["connector_label"] = "TBD"

    with pytest.raises(ValidationError, match="known value uses an unknown placeholder"):
        validate_document(document)


@pytest.mark.parametrize(
    ("entry_id", "pin", "channel", "signal", "polarity"),
    [
        ("pin_mapping.mks.pa9.green_gate", "PA9", "AF_GREEN", "GREEN LED gate", "positive"),
        ("pin_mapping.mks.pa10.red_gate", "PA10", "AF_RED", "RED LED gate", "positive"),
        ("pin_mapping.mks.pb13.white_gate", "PB13", "WHITE_BF", "WHITE LED gate", "positive"),
        ("pin_mapping.mks.pd6.camera_trigger", "PD6", "CAMERA_TRIGGER", "camera/sync trigger", None),
    ],
)
def test_known_rev_a5_assignments_validate_if_represented(
    example_document: dict,
    entry_id: str,
    pin: str,
    channel: str,
    signal: str,
    polarity: str | None,
) -> None:
    entry = copy.deepcopy(entry_by_id(example_document, entry_id))
    minimal_document = {
        "schema_version": "evidence-status/v1",
        "document_id": "minimal-known-pin-assignment",
        "description": "Minimal represented known assignment.",
        "required_unknowns": [],
        "entries": [entry],
    }

    value = entry["value"]
    assert value["pin"] == pin
    assert value["channel"] == channel
    assert value["signal"] == signal
    if polarity is not None:
        assert value["polarity"] == polarity

    validate_document(minimal_document)


def test_known_pin_assignment_mismatch_fails(example_document: dict) -> None:
    document = copy.deepcopy(example_document)
    entry = entry_by_id(document, "pin_mapping.mks.pa9.green_gate")
    entry["value"]["channel"] = "AF_RED"

    with pytest.raises(ValidationError, match="PA9 must be 'AF_GREEN'"):
        validate_document(document)


def test_rev_a5_no_guess_gate_requires_existing_unknown_entries(example_document: dict) -> None:
    document = copy.deepcopy(example_document)
    gate = next(
        gate
        for gate in document["live_action_gates"]
        if gate["id"] == "trigger_led_no_guess_gate"
    )
    gate["blocked_by"].append("output_type.missing")

    with pytest.raises(ValidationError, match="missing entry 'output_type.missing'"):
        validate_document(document)


def test_rev_a5_no_guess_gate_rejects_resolved_blocker(example_document: dict) -> None:
    document = copy.deepcopy(example_document)
    document["required_unknowns"].remove("output_type.camera_trigger")
    entry = entry_by_id(document, "output_type.camera_trigger")
    entry["status"] = "known"
    entry["value"] = {"output_type": "push-pull"}
    entry["evidence_refs"] = ["bench-notes.md"]
    entry.pop("unknown_reason", None)

    with pytest.raises(
        ValidationError,
        match=r"blocked_by: 'output_type.camera_trigger' must remain status 'unknown'",
    ):
        validate_document(document)


@pytest.mark.parametrize(
    "entry_id",
    [
        "encoder_part.x_axis",
        "encoder_signal_interface.counter_input_mapping",
        "encoder_calibration.image_transform",
        "approval.encoder_readiness",
    ],
)
def test_encoder_readiness_summary_unknowns_must_remain_unknown(
    encoder_document: dict, entry_id: str
) -> None:
    document = copy.deepcopy(encoder_document)
    document["required_unknowns"].remove(entry_id)
    entry = entry_by_id(document, entry_id)
    entry["status"] = "known"
    entry["value"] = {"unsafe_guess": True}
    entry["evidence_refs"] = ["bench-notes.md"]
    entry.pop("unknown_reason", None)

    with pytest.raises(ValidationError, match="must remain status 'unknown'"):
        validate_document(document)


def test_encoder_readiness_unknown_entry_must_not_carry_value(encoder_document: dict) -> None:
    document = copy.deepcopy(encoder_document)
    entry = entry_by_id(document, "encoder_part.resolution_counts_per_mm")
    entry["value"] = {"counts_per_mm": 1000}

    with pytest.raises(ValidationError, match="unknown entries must not carry values"):
        validate_document(document)


def test_blocker_summary_requires_existing_unknown_entries(encoder_document: dict) -> None:
    document = copy.deepcopy(encoder_document)
    document["unknown_blocker_summary"]["unknown_entry_ids"].append("encoder_part.missing_axis")
    blocker = document["unknown_blocker_summary"]["blockers"][0]
    blocker["blocked_by"].append("encoder_part.missing_axis")

    with pytest.raises(ValidationError, match="missing entry 'encoder_part.missing_axis'"):
        validate_document(document)


def test_blocker_summary_requires_entry_to_list_blocker(encoder_document: dict) -> None:
    document = copy.deepcopy(encoder_document)
    entry = entry_by_id(document, "encoder_part.x_axis")
    entry["blocks"] = []

    with pytest.raises(ValidationError, match="must list blocker 'encoder_part_selection'"):
        validate_document(document)


@pytest.mark.parametrize(
    "entry_id",
    [
        "controller_identity.exact_board_revision",
        "pin_mapping.motion.x_axis",
        "homing_capability.z_axis",
        "led_load_behavior.af_green",
        "camera_trigger_behavior.electrical_compatibility",
        "approval.pi_startup_hardware_evidence",
    ],
)
def test_pi_startup_unknowns_must_remain_unknown(
    pi_startup_document: dict, entry_id: str
) -> None:
    document = copy.deepcopy(pi_startup_document)
    entry = entry_by_id(document, entry_id)
    entry["status"] = "known"
    entry["value"] = {"unsafe_guess": True}
    entry["evidence_refs"] = ["bench-notes.md"]
    entry.pop("unknown_reason", None)

    with pytest.raises(ValidationError, match="must remain status 'unknown'"):
        validate_document(document)


def test_live_action_gate_requires_existing_unknown_entries(pi_startup_document: dict) -> None:
    document = copy.deepcopy(pi_startup_document)
    gate = document["live_action_gates"][0]
    gate["blocked_by"].append("controller_identity.missing")

    with pytest.raises(ValidationError, match="missing entry 'controller_identity.missing'"):
        validate_document(document)


def test_live_action_gate_rejects_known_blocker() -> None:
    document = {
        "schema_version": "evidence-status/v1",
        "document_id": "minimal-live-gate",
        "description": "Minimal live-action gate document.",
        "required_unknowns": [],
        "live_action_gates": [
            {
                "id": "no_motion_electrical_live_test_gate",
                "title": "No-motion electrical live test",
                "status": "prohibited_by_unknowns",
                "approved": False,
                "executed": False,
                "blocked_by": ["approval.no_motion_electrical_live_test"],
                "prohibited_actions": ["GPIO toggling"],
                "evidence_fields_required": ["reviewer approval"],
            }
        ],
        "entries": [
            {
                "id": "approval.no_motion_electrical_live_test",
                "category": "approval",
                "subject": "Approval for no-motion electrical live tests",
                "status": "known",
                "value": {"approved": True},
                "evidence_refs": ["bench-notes.md"],
            }
        ],
    }

    with pytest.raises(
        ValidationError,
        match=r"blocked_by: 'approval.no_motion_electrical_live_test' must remain status 'unknown'",
    ):
        validate_document(document)


def test_live_action_gate_rejects_empty_evidence_fields(pi_startup_document: dict) -> None:
    document = copy.deepcopy(pi_startup_document)
    gate = document["live_action_gates"][0]
    gate["evidence_fields_required"].append("")

    with pytest.raises(ValidationError, match="evidence_fields_required.*must not be empty"):
        validate_document(document)


@pytest.mark.parametrize("field", ["approved", "executed"])
def test_blocked_live_action_gate_must_not_be_approved_or_executed(
    pi_startup_document: dict, field: str
) -> None:
    document = copy.deepcopy(pi_startup_document)
    gate = document["live_action_gates"][0]
    gate[field] = True

    with pytest.raises(ValidationError, match=rf"{field}: prohibited gate must be false"):
        validate_document(document)


def test_pi_startup_has_closed_stage_live_test_gates(pi_startup_document: dict) -> None:
    gates_by_id = {gate["id"]: gate for gate in pi_startup_document["live_action_gates"]}

    for gate_id in [
        "no_load_output_live_test_gate",
        "led_live_test_gate",
        "camera_trigger_live_test_gate",
        "motion_live_test_gate",
        "homing_live_test_gate",
    ]:
        gate = gates_by_id[gate_id]
        assert gate["status"] == "prohibited_by_unknowns"
        assert gate["approved"] is False
        assert gate["executed"] is False


@pytest.mark.parametrize(
    "entry_id",
    [
        "driver_capability.x_axis",
        "endstop_input.x_axis",
        "homing_capability.x_axis",
        "sensorless_feasibility.x_axis",
        "test_prerequisite.no_motion_homing_readiness",
        "test_prerequisite.one_axis_low_speed_motion",
        "approval.homing_readiness",
    ],
)
def test_homing_readiness_unknowns_must_remain_unknown(
    homing_document: dict, entry_id: str
) -> None:
    document = copy.deepcopy(homing_document)
    entry = entry_by_id(document, entry_id)
    entry["status"] = "known"
    entry["value"] = {"unsafe_guess": True}
    entry["evidence_refs"] = ["bench-notes.md"]
    entry.pop("unknown_reason", None)

    with pytest.raises(ValidationError, match="must remain status 'unknown'"):
        validate_document(document)


def test_homing_sensorless_gate_rejects_unsupported_known_guess(
    homing_document: dict,
) -> None:
    document = copy.deepcopy(homing_document)
    document["required_unknowns"].remove("sensorless_feasibility.x_axis")
    entry = entry_by_id(document, "sensorless_feasibility.x_axis")
    entry["status"] = "known"
    entry["value"] = {
        "outcome": "candidate_with_limits",
        "feedback": "assumed from driver family",
    }
    entry["evidence_refs"] = ["bench-notes.md"]
    entry.pop("unknown_reason", None)

    with pytest.raises(
        ValidationError,
        match=r"unknown_entry_ids: 'sensorless_feasibility.x_axis' must remain status 'unknown'",
    ):
        validate_document(document)


def test_homing_one_axis_live_gate_requires_prerequisite_unknown(
    homing_document: dict,
) -> None:
    document = copy.deepcopy(homing_document)
    gate = next(
        gate
        for gate in document["live_action_gates"]
        if gate["id"] == "one_axis_low_speed_motion_gate"
    )
    gate["blocked_by"].append("test_prerequisite.missing_motion_test")

    with pytest.raises(
        ValidationError,
        match="missing entry 'test_prerequisite.missing_motion_test'",
    ):
        validate_document(document)


@pytest.mark.parametrize(
    "entry_id",
    [
        "controller_identity.exact_mks_kingroon_variant_relationship",
        "controller_identity.exact_mcu_part",
        "firmware_path.flash_debug_method",
        "pin_mapping.motion.x_axis",
        "pin_mapping.motion.y_axis",
        "pin_mapping.motion.z_axis",
        "pin_mapping.endstop_inputs",
        "output_state.controller_boot_reset",
        "output_state.candidate_outputs_at_boot",
        "approval.pinmap_verification",
        "approval.motion_or_homing_live_test",
    ],
)
def test_controller_discovery_unknowns_must_remain_unknown(
    controller_document: dict, entry_id: str
) -> None:
    document = copy.deepcopy(controller_document)
    entry = entry_by_id(document, entry_id)
    entry["status"] = "known"
    entry["value"] = {"unsafe_guess": True}
    entry["evidence_refs"] = ["bench-notes.md"]
    entry.pop("unknown_reason", None)

    with pytest.raises(ValidationError, match="must remain status 'unknown'"):
        validate_document(document)


def test_controller_profile_remains_pinmap_candidate(controller_document: dict) -> None:
    entry = entry_by_id(controller_document, "controller_identity.board_profile_state")
    assert entry["value"]["profile_state"] == "pinmap_candidate"
    assert entry["value"]["hardware_approval"] is False
    assert entry["value"]["simulator_only_until"] == "pinmap_verified"
    assert entry["value"]["homing_configured"] is False
    assert entry["value"]["limit_switches_connected"] is False
    assert (
        entry["value"]["homing_enable_gate"]
        == "disabled_until_pinmap_verified_and_homing_evidence_reviewed"
    )
    assert (
        entry["value"]["future_boundary_detection"]
        == "pico_or_driver_based_possible_not_proven"
    )


def test_controller_has_pending_stage0_stage1_no_output_proposals(
    controller_document: dict,
) -> None:
    proposals_by_id = {
        proposal["id"]: proposal for proposal in controller_document["procedure_proposals"]
    }

    assert set(proposals_by_id) == {
        "stage0_read_only_inspection_proposal",
        "stage1_dummy_no_load_preflight_proposal",
    }
    for proposal in proposals_by_id.values():
        assert proposal["proposal_status"] == "proposal_pending_approval"
        assert proposal["approved"] is False
        assert proposal["executed"] is False
        assert proposal["hardware_access"] == "software_only"
        assert proposal["output_mode"] == "none"
        assert proposal["evidence_refs"] == []

    stage1 = proposals_by_id["stage1_dummy_no_load_preflight_proposal"]
    assert stage1["depends_on"] == ["stage0_read_only_inspection_proposal"]


@pytest.mark.parametrize("field", ["approved", "executed"])
def test_pending_procedure_proposal_must_not_be_approved_or_executed(
    controller_document: dict, field: str
) -> None:
    document = copy.deepcopy(controller_document)
    proposal = proposal_by_id(document, "stage0_read_only_inspection_proposal")
    proposal[field] = True

    with pytest.raises(ValidationError, match=rf"{field}: pending proposal must be false"):
        validate_document(document)


def test_pending_procedure_proposal_must_not_have_evidence_refs(
    controller_document: dict,
) -> None:
    document = copy.deepcopy(controller_document)
    proposal = proposal_by_id(document, "stage0_read_only_inspection_proposal")
    proposal["evidence_refs"] = ["approval-record.md"]

    with pytest.raises(ValidationError, match="pending proposal must be empty"):
        validate_document(document)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("hardware_access", "live_controller", "hardware_access: must be software_only"),
        ("output_mode", "gpio", "output_mode: must be none"),
    ],
)
def test_procedure_proposal_rejects_live_access_or_output_mode(
    controller_document: dict, field: str, value: str, message: str
) -> None:
    document = copy.deepcopy(controller_document)
    proposal = proposal_by_id(document, "stage1_dummy_no_load_preflight_proposal")
    proposal[field] = value

    with pytest.raises(ValidationError, match=message):
        validate_document(document)


def test_approved_procedure_proposal_requires_evidence_refs(
    controller_document: dict,
) -> None:
    document = copy.deepcopy(controller_document)
    proposal = proposal_by_id(document, "stage0_read_only_inspection_proposal")
    proposal["proposal_status"] = "approved_pending_execution"
    proposal["approved"] = True

    with pytest.raises(ValidationError, match="approved proposal requires evidence"):
        validate_document(document)


def test_current_a4988_driver_does_not_provide_sensorless_homing(
    controller_document: dict,
) -> None:
    entry = entry_by_id(controller_document, "driver_capability.mks_a4988_sensorless")
    assert entry["value"]["driver_type"] == "A4988"
    assert entry["value"]["sensorless_feedback"] == "none_documented"
    assert entry["value"]["homing_capability"] == "not_supported_by_current_evidence"


def test_pi_startup_evidence_projects_to_software_only_telemetry(
    pi_startup_document: dict,
) -> None:
    records = project_evidence_to_telemetry_records(pi_startup_document)

    validate_telemetry_records(records)
    assert records[0]["event_name"] == "evidence_ledger_written"
    assert all(record["hardware_outputs_enabled"] is False for record in records)
    assert all(record["live_hardware_access_used"] is False for record in records)

    ledger_payload = records[0]["payload"]
    assert ledger_payload["document_id"] == "pi-startup-hardware-evidence-status"
    assert "approval.pi_startup_hardware_evidence" in ledger_payload[
        "required_unknown_entry_ids"
    ]
    assert "pi_startup_hardware_evidence_unknown" in ledger_payload["blocker_ids"]
    assert "no_motion_electrical_live_test_gate" in ledger_payload[
        "blocked_live_action_gate_ids"
    ]

    gate_records = [
        record for record in records if record["event_name"] == "safety_gate_blocked"
    ]
    assert {
        record["payload"]["gate_id"] for record in gate_records
    } == {
        gate["id"]
        for gate in pi_startup_document["live_action_gates"]
        if gate["status"] == "prohibited_by_unknowns"
    }
    first_gate_payload = gate_records[0]["payload"]
    assert first_gate_payload["blocked_by_unknown_entry_ids"] == pi_startup_document[
        "live_action_gates"
    ][0]["blocked_by"]
    assert first_gate_payload["approved"] is False
    assert first_gate_payload["executed"] is False


def test_controller_projection_preserves_hardware_disabled_flags(
    controller_document: dict,
) -> None:
    records = project_evidence_to_telemetry_records(controller_document)
    ledger_flags = records[0]["payload"]["hardware_disabled_flags"]

    assert {
        (flag["entry_id"], flag["field"], flag["value"]) for flag in ledger_flags
    } >= {
        ("controller_identity.board_profile_state", "hardware_approval", False),
        (
            "controller_identity.board_profile_state",
            "simulator_only_until",
            "pinmap_verified",
        ),
        ("controller_identity.board_profile_state", "homing_configured", False),
        ("controller_identity.board_profile_state", "limit_switches_connected", False),
    }


def test_projection_preserves_related_blocker_ids(controller_document: dict) -> None:
    records = project_evidence_to_telemetry_records(controller_document)
    gate_record = next(
        record
        for record in records
        if record["event_name"] == "safety_gate_blocked"
        and record["payload"]["gate_id"] == "controller_no_motion_electrical_gate"
    )

    assert gate_record["payload"]["related_blocker_ids"] == [
        "pinmap_verified_state_blocked"
    ]


def test_projection_rejects_hardware_enabled_telemetry(
    pi_startup_document: dict,
) -> None:
    records = project_evidence_to_telemetry_records(pi_startup_document)
    records[0] = dict(records[0], hardware_outputs_enabled=True)

    with pytest.raises(TelemetryProjectionError, match="hardware_outputs_enabled"):
        validate_telemetry_records(records)


def test_projection_validates_evidence_before_emitting(
    pi_startup_document: dict,
) -> None:
    document = copy.deepcopy(pi_startup_document)
    entry = entry_by_id(document, "approval.pi_startup_hardware_evidence")
    entry["status"] = "known"
    entry["value"] = {"unsafe_guess": True}
    entry["evidence_refs"] = ["bench-notes.md"]
    entry.pop("unknown_reason", None)

    with pytest.raises(ValidationError, match="must remain status 'unknown'"):
        project_evidence_to_telemetry_records(document)


def test_cli_can_emit_telemetry_jsonl(capsys: pytest.CaptureFixture[str]) -> None:
    result = main(["--emit-telemetry-jsonl", str(CONTROLLER_EXAMPLE_PATH)])

    assert result == 0
    captured = capsys.readouterr()
    records = [json.loads(line) for line in captured.out.splitlines()]
    assert captured.err == ""
    assert records[0]["event_name"] == "evidence_ledger_written"
    gate_ids = [
        record["payload"]["gate_id"]
        for record in records[1:]
        if record["event_name"] == "safety_gate_blocked"
    ]
    assert gate_ids == [
        "controller_no_motion_electrical_gate",
        "controller_motion_homing_gate",
        "controller_v1_manual_centered_bounded_test_gate",
    ]
    validate_telemetry_records(records)
