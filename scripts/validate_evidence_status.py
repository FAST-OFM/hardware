#!/usr/bin/env python3
"""Validate scanner-hardware evidence status JSON files.

This validator is intentionally offline-only. It reads documentation/data files
and never touches GPIO, serial ports, network resources, firmware, or hardware.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "evidence-status/v1"
TELEMETRY_SCHEMA_ID = "scanner_pi.telemetry_event"
TELEMETRY_SCHEMA_VERSION = "1.0.0"
TELEMETRY_SOURCE_COMPONENT = "scanner-hardware.evidence_status_projection"

CATEGORIES = {
    "led_current_limit",
    "test_prerequisite",
    "rail_limit",
    "pin_mapping",
    "output_type",
    "output_state",
    "controller_identity",
    "driver_capability",
    "endstop_input",
    "firmware_path",
    "homing_capability",
    "sensorless_feasibility",
    "led_load_behavior",
    "camera_trigger_behavior",
    "encoder_part",
    "encoder_mechanical_mount",
    "encoder_signal_interface",
    "encoder_calibration",
    "approval",
}
STATUSES = {"known", "unknown", "not_applicable"}
TELEMETRY_EVENT_NAMES = {"evidence_ledger_written", "safety_gate_blocked"}
TELEMETRY_SEVERITIES = {"debug", "info", "warning", "error", "critical"}
TELEMETRY_REQUIRED_FIELDS = {
    "schema_id",
    "schema_version",
    "event_name",
    "source_component",
    "severity",
    "hardware_outputs_enabled",
    "live_hardware_access_used",
    "payload",
}
TELEMETRY_ALLOWED_FIELDS = TELEMETRY_REQUIRED_FIELDS | {
    "run_id",
    "scan_id",
    "frame_id",
    "stripe_id",
    "stripe_frame_index",
    "command_id",
    "calibration_id",
    "host_monotonic_ns",
    "host_wall_time_iso8601",
    "mcu_time_us",
    "camera_sensor_timestamp_ns",
    "camera_sequence",
}
TELEMETRY_FORBIDDEN_PAYLOAD_FIELDS = {
    "device_path",
    "firmware_flash",
    "gcode",
    "gpio",
    "gpio_pin",
    "hardware_command",
    "led_output",
    "move_z_now",
    "network_endpoint",
    "serial_port",
}
TELEMETRY_UNSAFE_PAYLOAD_BOOLEAN_FIELDS = {
    "contains_hardware_commands",
    "hardware_outputs_enabled",
    "live_hardware_access_used",
    "may_access_gpio",
    "may_command_motion",
    "may_emit_led_output",
    "may_flash_firmware",
    "may_move_stage",
    "may_open_camera",
    "may_open_network",
    "may_open_serial_port",
}
HARDWARE_DISABLED_FLAG_FIELDS = {
    "approved_use",
    "hardware_approval",
    "hardware_outputs_enabled",
    "homing_configured",
    "live_hardware_access_used",
    "limit_switches_connected",
    "simulator_only_until",
}
UNKNOWN_TOKENS = {
    "",
    "unknown",
    "unk",
    "tbd",
    "tba",
    "todo",
    "not measured",
    "unmeasured",
    "to be measured",
    "not verified",
}

EXPECTED_PIN_ASSIGNMENTS: dict[str, dict[str, str]] = {
    "PA9": {
        "channel": "AF_GREEN",
        "signal": "GREEN LED gate",
        "polarity": "positive",
    },
    "PA10": {
        "channel": "AF_RED",
        "signal": "RED LED gate",
        "polarity": "positive",
    },
    "PB13": {
        "channel": "WHITE_BF",
        "signal": "WHITE LED gate",
        "polarity": "positive",
    },
    "PD6": {
        "channel": "CAMERA_TRIGGER",
        "signal": "camera/sync trigger",
    },
}


class ValidationError(Exception):
    """Raised when an evidence status document is invalid."""


class TelemetryProjectionError(Exception):
    """Raised when an evidence-to-telemetry projection is invalid."""


def _expect_type(value: Any, expected_type: type, path: str) -> None:
    if not isinstance(value, expected_type):
        raise ValidationError(f"{path}: expected {expected_type.__name__}")


def _require_keys(mapping: dict[str, Any], keys: set[str], path: str) -> None:
    missing = sorted(keys - mapping.keys())
    if missing:
        raise ValidationError(f"{path}: missing required key(s): {', '.join(missing)}")


def _is_unknown_token(value: str) -> bool:
    return value.strip().lower() in UNKNOWN_TOKENS


def _reject_placeholder_known_values(value: Any, path: str) -> None:
    if isinstance(value, str):
        if _is_unknown_token(value):
            raise ValidationError(f"{path}: known value uses an unknown placeholder")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            _reject_placeholder_known_values(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _reject_placeholder_known_values(child, f"{path}[{index}]")
        return
    if value is None:
        raise ValidationError(f"{path}: known value must not be null")


def _validate_string_list(value: Any, path: str) -> None:
    _expect_type(value, list, path)
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        _expect_type(item, str, item_path)
        if not item:
            raise ValidationError(f"{item_path}: must not be empty")
        if item in seen:
            raise ValidationError(f"{item_path}: duplicate value {item!r}")
        seen.add(item)


def _validate_known_pin_assignment(entry: dict[str, Any], path: str) -> None:
    if entry["category"] != "pin_mapping" or entry["status"] != "known":
        return

    value = entry.get("value")
    if not isinstance(value, dict):
        raise ValidationError(f"{path}.value: known pin_mapping value must be an object")

    pin = value.get("pin")
    if pin not in EXPECTED_PIN_ASSIGNMENTS:
        return

    expected = EXPECTED_PIN_ASSIGNMENTS[pin]
    for key, expected_value in expected.items():
        actual_value = value.get(key)
        if actual_value != expected_value:
            raise ValidationError(
                f"{path}.value.{key}: {pin} must be {expected_value!r}, got {actual_value!r}"
            )


def _validate_blocker_summary(
    summary: Any, entries_by_id: dict[str, dict[str, Any]], path: str
) -> None:
    _expect_type(summary, dict, path)
    allowed_keys = {
        "scope",
        "summary_status",
        "unknown_entry_ids",
        "blockers",
    }
    extra = sorted(set(summary) - allowed_keys)
    if extra:
        raise ValidationError(f"{path}: unknown key(s): {', '.join(extra)}")
    _require_keys(summary, allowed_keys, path)

    _expect_type(summary["scope"], str, f"{path}.scope")
    if not summary["scope"]:
        raise ValidationError(f"{path}.scope: must not be empty")

    _expect_type(summary["summary_status"], str, f"{path}.summary_status")
    if summary["summary_status"] not in {"blocked_by_unknowns", "ready", "not_applicable"}:
        raise ValidationError(
            f"{path}.summary_status: unsupported status {summary['summary_status']!r}"
        )

    _validate_string_list(summary["unknown_entry_ids"], f"{path}.unknown_entry_ids")
    unknown_entry_ids = set(summary["unknown_entry_ids"])
    for entry_id in summary["unknown_entry_ids"]:
        entry = entries_by_id.get(entry_id)
        if entry is None:
            raise ValidationError(f"{path}.unknown_entry_ids: missing entry {entry_id!r}")
        if entry["status"] != "unknown":
            raise ValidationError(
                f"{path}.unknown_entry_ids: {entry_id!r} must remain status 'unknown'"
            )

    _expect_type(summary["blockers"], list, f"{path}.blockers")
    if summary["summary_status"] == "blocked_by_unknowns" and not summary["blockers"]:
        raise ValidationError(f"{path}.blockers: blocked summary requires blockers")

    blocker_ids: set[str] = set()
    for index, blocker in enumerate(summary["blockers"]):
        blocker_path = f"{path}.blockers[{index}]"
        _expect_type(blocker, dict, blocker_path)
        allowed_blocker_keys = {
            "id",
            "title",
            "blocked_by",
            "blocks",
            "resolution_evidence_required",
            "evidence_fields_required",
        }
        extra = sorted(set(blocker) - allowed_blocker_keys)
        if extra:
            raise ValidationError(f"{blocker_path}: unknown key(s): {', '.join(extra)}")
        _require_keys(
            blocker,
            {"id", "title", "blocked_by", "blocks", "resolution_evidence_required"},
            blocker_path,
        )

        for key in ("id", "title", "resolution_evidence_required"):
            _expect_type(blocker[key], str, f"{blocker_path}.{key}")
            if not blocker[key]:
                raise ValidationError(f"{blocker_path}.{key}: must not be empty")

        if blocker["id"] in blocker_ids:
            raise ValidationError(f"{blocker_path}.id: duplicate id {blocker['id']!r}")
        blocker_ids.add(blocker["id"])

        _validate_string_list(blocker["blocked_by"], f"{blocker_path}.blocked_by")
        _validate_string_list(blocker["blocks"], f"{blocker_path}.blocks")
        if "evidence_fields_required" in blocker:
            _validate_string_list(
                blocker["evidence_fields_required"],
                f"{blocker_path}.evidence_fields_required",
            )
        for entry_id in blocker["blocked_by"]:
            if entry_id not in unknown_entry_ids:
                raise ValidationError(
                    f"{blocker_path}.blocked_by: {entry_id!r} is not summarized "
                    "in unknown_entry_ids"
                )
            entry = entries_by_id[entry_id]
            if entry["status"] != "unknown":
                raise ValidationError(
                    f"{blocker_path}.blocked_by: {entry_id!r} must remain status 'unknown'"
                )
            if blocker["id"] not in entry.get("blocks", []):
                raise ValidationError(
                    f"{blocker_path}.blocked_by: {entry_id!r} must list blocker "
                    f"{blocker['id']!r} in entry.blocks"
                )


def _validate_live_action_gates(
    gates: Any, entries_by_id: dict[str, dict[str, Any]], path: str
) -> None:
    _expect_type(gates, list, path)
    gate_ids: set[str] = set()
    for index, gate in enumerate(gates):
        gate_path = f"{path}[{index}]"
        _expect_type(gate, dict, gate_path)
        allowed_keys = {
            "id",
            "title",
            "status",
            "approved",
            "executed",
            "blocked_by",
            "prohibited_actions",
            "evidence_fields_required",
        }
        extra = sorted(set(gate) - allowed_keys)
        if extra:
            raise ValidationError(f"{gate_path}: unknown key(s): {', '.join(extra)}")
        _require_keys(gate, allowed_keys, gate_path)

        for key in ("id", "title", "status"):
            _expect_type(gate[key], str, f"{gate_path}.{key}")
            if not gate[key]:
                raise ValidationError(f"{gate_path}.{key}: must not be empty")

        if gate["id"] in gate_ids:
            raise ValidationError(f"{gate_path}.id: duplicate id {gate['id']!r}")
        gate_ids.add(gate["id"])

        if gate["status"] not in {
            "prohibited_by_unknowns",
            "pending_review",
            "not_applicable",
        }:
            raise ValidationError(f"{gate_path}.status: unsupported status {gate['status']!r}")
        for key in ("approved", "executed"):
            if not isinstance(gate[key], bool):
                raise ValidationError(f"{gate_path}.{key}: expected bool")

        _validate_string_list(gate["blocked_by"], f"{gate_path}.blocked_by")
        _validate_string_list(gate["prohibited_actions"], f"{gate_path}.prohibited_actions")
        _validate_string_list(
            gate["evidence_fields_required"], f"{gate_path}.evidence_fields_required"
        )
        if gate["status"] == "prohibited_by_unknowns" and not gate["blocked_by"]:
            raise ValidationError(f"{gate_path}.blocked_by: prohibited gate requires blockers")
        if gate["status"] == "prohibited_by_unknowns":
            if gate["approved"] is not False:
                raise ValidationError(
                    f"{gate_path}.approved: prohibited gate must be false"
                )
            if gate["executed"] is not False:
                raise ValidationError(
                    f"{gate_path}.executed: prohibited gate must be false"
                )

        for entry_id in gate["blocked_by"]:
            entry = entries_by_id.get(entry_id)
            if entry is None:
                raise ValidationError(f"{gate_path}.blocked_by: missing entry {entry_id!r}")
            if gate["status"] == "prohibited_by_unknowns" and entry["status"] != "unknown":
                raise ValidationError(
                    f"{gate_path}.blocked_by: {entry_id!r} must remain status 'unknown'"
                )


def _validate_procedure_proposals(proposals: Any, path: str) -> None:
    _expect_type(proposals, list, path)
    proposal_ids: set[str] = set()
    for index, proposal in enumerate(proposals):
        proposal_path = f"{path}[{index}]"
        _expect_type(proposal, dict, proposal_path)
        allowed_keys = {
            "id",
            "title",
            "stage",
            "proposal_status",
            "approved",
            "executed",
            "hardware_access",
            "output_mode",
            "scope",
            "depends_on",
            "allowed_actions",
            "prohibited_actions",
            "approval_required",
            "evidence_refs",
            "evidence_fields_required",
        }
        extra = sorted(set(proposal) - allowed_keys)
        if extra:
            raise ValidationError(f"{proposal_path}: unknown key(s): {', '.join(extra)}")
        _require_keys(proposal, allowed_keys, proposal_path)

        for key in (
            "id",
            "title",
            "stage",
            "proposal_status",
            "hardware_access",
            "output_mode",
            "scope",
            "approval_required",
        ):
            _expect_type(proposal[key], str, f"{proposal_path}.{key}")
            if not proposal[key]:
                raise ValidationError(f"{proposal_path}.{key}: must not be empty")

        if proposal["id"] in proposal_ids:
            raise ValidationError(f"{proposal_path}.id: duplicate id {proposal['id']!r}")
        proposal_ids.add(proposal["id"])

        if proposal["stage"] not in {"stage_0", "stage_1"}:
            raise ValidationError(
                f"{proposal_path}.stage: unsupported stage {proposal['stage']!r}"
            )
        if proposal["proposal_status"] not in {
            "proposal_pending_approval",
            "approved_pending_execution",
            "executed",
            "rejected",
        }:
            raise ValidationError(
                f"{proposal_path}.proposal_status: unsupported status "
                f"{proposal['proposal_status']!r}"
            )
        for key in ("approved", "executed"):
            if not isinstance(proposal[key], bool):
                raise ValidationError(f"{proposal_path}.{key}: expected bool")

        if proposal["hardware_access"] != "software_only":
            raise ValidationError(f"{proposal_path}.hardware_access: must be software_only")
        if proposal["output_mode"] != "none":
            raise ValidationError(f"{proposal_path}.output_mode: must be none")

        _validate_string_list(proposal["depends_on"], f"{proposal_path}.depends_on")
        _validate_string_list(
            proposal["allowed_actions"], f"{proposal_path}.allowed_actions"
        )
        _validate_string_list(
            proposal["prohibited_actions"], f"{proposal_path}.prohibited_actions"
        )
        _validate_string_list(proposal["evidence_refs"], f"{proposal_path}.evidence_refs")
        _validate_string_list(
            proposal["evidence_fields_required"],
            f"{proposal_path}.evidence_fields_required",
        )
        if not proposal["allowed_actions"]:
            raise ValidationError(f"{proposal_path}.allowed_actions: must not be empty")
        if not proposal["prohibited_actions"]:
            raise ValidationError(f"{proposal_path}.prohibited_actions: must not be empty")
        if not proposal["evidence_fields_required"]:
            raise ValidationError(
                f"{proposal_path}.evidence_fields_required: must not be empty"
            )

        status = proposal["proposal_status"]
        if status == "proposal_pending_approval":
            if proposal["approved"] is not False:
                raise ValidationError(
                    f"{proposal_path}.approved: pending proposal must be false"
                )
            if proposal["executed"] is not False:
                raise ValidationError(
                    f"{proposal_path}.executed: pending proposal must be false"
                )
            if proposal["evidence_refs"]:
                raise ValidationError(
                    f"{proposal_path}.evidence_refs: pending proposal must be empty "
                    "until human approval exists"
                )
        elif status == "approved_pending_execution":
            if proposal["approved"] is not True:
                raise ValidationError(
                    f"{proposal_path}.approved: approved proposal must be true"
                )
            if proposal["executed"] is not False:
                raise ValidationError(
                    f"{proposal_path}.executed: approved pending proposal must be false"
                )
            if not proposal["evidence_refs"]:
                raise ValidationError(
                    f"{proposal_path}.evidence_refs: approved proposal requires evidence"
                )
        elif status == "executed":
            if proposal["approved"] is not True:
                raise ValidationError(
                    f"{proposal_path}.approved: executed proposal must be approved"
                )
            if proposal["executed"] is not True:
                raise ValidationError(
                    f"{proposal_path}.executed: executed proposal must be true"
                )
            if not proposal["evidence_refs"]:
                raise ValidationError(
                    f"{proposal_path}.evidence_refs: executed proposal requires evidence"
                )
        elif proposal["approved"] or proposal["executed"]:
            raise ValidationError(
                f"{proposal_path}.proposal_status: rejected proposal must not be "
                "approved or executed"
            )


def _gate_related_blocker_ids(
    gate: dict[str, Any], unknown_blocker_summary: Any
) -> list[str]:
    if not isinstance(unknown_blocker_summary, dict):
        return []

    gate_blocked_by = set(gate["blocked_by"])
    related: list[str] = []
    for blocker in unknown_blocker_summary.get("blockers", []):
        if not isinstance(blocker, dict):
            continue
        blocked_by = blocker.get("blocked_by", [])
        if not isinstance(blocked_by, list):
            continue
        if gate_blocked_by.intersection(blocked_by):
            related.append(blocker["id"])
    return related


def _extract_hardware_disabled_flags(document: dict[str, Any]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for entry in document["entries"]:
        value = entry.get("value")
        if not isinstance(value, dict):
            continue
        for field in sorted(HARDWARE_DISABLED_FLAG_FIELDS.intersection(value)):
            flags.append(
                {
                    "entry_id": entry["id"],
                    "field": field,
                    "value": value[field],
                }
            )
    return flags


def _make_telemetry_record(
    event_name: str,
    *,
    severity: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    record = {
        "schema_id": TELEMETRY_SCHEMA_ID,
        "schema_version": TELEMETRY_SCHEMA_VERSION,
        "event_name": event_name,
        "source_component": TELEMETRY_SOURCE_COMPONENT,
        "severity": severity,
        "hardware_outputs_enabled": False,
        "live_hardware_access_used": False,
        "payload": payload,
    }
    validate_telemetry_record(record)
    return record


def project_evidence_to_telemetry_records(document: Any) -> list[dict[str, Any]]:
    """Project one validated evidence document to software-only telemetry records."""

    validate_document(document)
    unknown_entry_ids = [
        entry["id"] for entry in document["entries"] if entry["status"] == "unknown"
    ]
    live_action_gates = document.get("live_action_gates", [])
    procedure_proposals = document.get("procedure_proposals", [])
    blocked_live_action_gates = [
        gate for gate in live_action_gates if gate["status"] == "prohibited_by_unknowns"
    ]
    unknown_blocker_summary = document.get("unknown_blocker_summary")
    blockers = []
    if isinstance(unknown_blocker_summary, dict):
        blockers = unknown_blocker_summary.get("blockers", [])

    records = [
        _make_telemetry_record(
            "evidence_ledger_written",
            severity="warning" if document["required_unknowns"] else "info",
            payload={
                "document_id": document["document_id"],
                "evidence_schema_version": document["schema_version"],
                "projection_mode": "offline_checked_in_evidence",
                "required_unknown_entry_ids": list(document["required_unknowns"]),
                "unknown_entry_ids": unknown_entry_ids,
                "blocker_ids": [blocker["id"] for blocker in blockers],
                "live_action_gate_ids": [gate["id"] for gate in live_action_gates],
                "procedure_proposal_ids": [
                    proposal["id"] for proposal in procedure_proposals
                ],
                "pending_procedure_proposal_ids": [
                    proposal["id"]
                    for proposal in procedure_proposals
                    if proposal["proposal_status"] == "proposal_pending_approval"
                ],
                "blocked_live_action_gate_ids": [
                    gate["id"] for gate in blocked_live_action_gates
                ],
                "hardware_disabled_flags": _extract_hardware_disabled_flags(document),
            },
        )
    ]

    for gate in blocked_live_action_gates:
        records.append(
            _make_telemetry_record(
                "safety_gate_blocked",
                severity="warning",
                payload={
                    "document_id": document["document_id"],
                    "gate_id": gate["id"],
                    "gate_title": gate["title"],
                    "gate_status": gate["status"],
                    "approved": gate["approved"],
                    "executed": gate["executed"],
                    "blocked_by_unknown_entry_ids": list(gate["blocked_by"]),
                    "related_blocker_ids": _gate_related_blocker_ids(
                        gate, unknown_blocker_summary
                    ),
                    "prohibited_actions": list(gate["prohibited_actions"]),
                    "evidence_fields_required": list(gate["evidence_fields_required"]),
                },
            )
        )

    return records


def _reject_non_json_value(value: Any, path: str) -> None:
    try:
        json.dumps(value, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise TelemetryProjectionError(f"{path} must be JSON serializable") from exc


def _reject_control_plane_payload_fields(
    payload: dict[str, Any], path: str = "payload"
) -> None:
    for key, value in payload.items():
        key_text = str(key)
        normalized_key = key_text.lower()
        child_path = f"{path}.{key_text}"
        if normalized_key in TELEMETRY_FORBIDDEN_PAYLOAD_FIELDS:
            raise TelemetryProjectionError(f"{child_path} is forbidden")
        if normalized_key in TELEMETRY_UNSAFE_PAYLOAD_BOOLEAN_FIELDS and value is not False:
            raise TelemetryProjectionError(f"{child_path} must be false")
        if isinstance(value, dict):
            _reject_control_plane_payload_fields(value, child_path)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    _reject_control_plane_payload_fields(item, f"{child_path}[{index}]")


def validate_telemetry_record(record: Any) -> None:
    _expect_type(record, dict, "telemetry")
    missing = sorted(TELEMETRY_REQUIRED_FIELDS - record.keys())
    if missing:
        raise TelemetryProjectionError(
            "telemetry: missing required field(s): " + ", ".join(missing)
        )
    extra = sorted(set(record) - TELEMETRY_ALLOWED_FIELDS)
    if extra:
        raise TelemetryProjectionError(
            "telemetry: unknown field(s): " + ", ".join(extra)
        )

    for key in ("schema_id", "schema_version", "event_name", "source_component", "severity"):
        if not isinstance(record[key], str) or not record[key]:
            raise TelemetryProjectionError(f"telemetry.{key}: must be a non-empty string")
    if record["schema_id"] != TELEMETRY_SCHEMA_ID:
        raise TelemetryProjectionError(
            f"telemetry.schema_id: expected {TELEMETRY_SCHEMA_ID!r}"
        )
    if record["schema_version"] != TELEMETRY_SCHEMA_VERSION:
        raise TelemetryProjectionError(
            f"telemetry.schema_version: expected {TELEMETRY_SCHEMA_VERSION!r}"
        )
    if record["event_name"] not in TELEMETRY_EVENT_NAMES:
        raise TelemetryProjectionError(
            f"telemetry.event_name: unsupported event {record['event_name']!r}"
        )
    if record["severity"] not in TELEMETRY_SEVERITIES:
        raise TelemetryProjectionError(
            f"telemetry.severity: unsupported severity {record['severity']!r}"
        )
    if record["hardware_outputs_enabled"] is not False:
        raise TelemetryProjectionError("telemetry.hardware_outputs_enabled must be false")
    if record["live_hardware_access_used"] is not False:
        raise TelemetryProjectionError("telemetry.live_hardware_access_used must be false")
    if not isinstance(record["payload"], dict):
        raise TelemetryProjectionError("telemetry.payload: must be an object")

    _reject_control_plane_payload_fields(record["payload"])
    _reject_non_json_value(record, "telemetry")


def validate_telemetry_records(records: Any) -> None:
    _expect_type(records, list, "telemetry_records")
    if not records:
        raise TelemetryProjectionError("telemetry_records: must not be empty")
    for index, record in enumerate(records):
        try:
            validate_telemetry_record(record)
        except TelemetryProjectionError as exc:
            raise TelemetryProjectionError(f"telemetry_records[{index}]: {exc}") from exc


def _validate_entry(entry: Any, path: str) -> str:
    _expect_type(entry, dict, path)
    allowed_keys = {
        "id",
        "category",
        "subject",
        "status",
        "value",
        "unknown_reason",
        "rationale",
        "evidence_refs",
        "blocks",
        "evidence_fields_required",
    }
    extra = sorted(set(entry) - allowed_keys)
    if extra:
        raise ValidationError(f"{path}: unknown key(s): {', '.join(extra)}")

    _require_keys(entry, {"id", "category", "subject", "status", "evidence_refs"}, path)

    for key in ("id", "category", "subject", "status"):
        _expect_type(entry[key], str, f"{path}.{key}")

    entry_id = entry["id"]
    if not entry_id:
        raise ValidationError(f"{path}.id: must not be empty")

    if entry["category"] not in CATEGORIES:
        raise ValidationError(f"{path}.category: unsupported category {entry['category']!r}")
    if entry["status"] not in STATUSES:
        raise ValidationError(f"{path}.status: unsupported status {entry['status']!r}")

    _validate_string_list(entry["evidence_refs"], f"{path}.evidence_refs")
    if "blocks" in entry:
        _validate_string_list(entry["blocks"], f"{path}.blocks")
    if "evidence_fields_required" in entry:
        _validate_string_list(entry["evidence_fields_required"], f"{path}.evidence_fields_required")

    status = entry["status"]
    if status == "unknown":
        if "unknown_reason" not in entry:
            raise ValidationError(f"{path}.unknown_reason: required for unknown status")
        _expect_type(entry["unknown_reason"], str, f"{path}.unknown_reason")
        if not entry["unknown_reason"]:
            raise ValidationError(f"{path}.unknown_reason: must not be empty")
        if "value" in entry:
            raise ValidationError(f"{path}.value: unknown entries must not carry values")
        if "rationale" in entry:
            raise ValidationError(f"{path}.rationale: use unknown_reason for unknown entries")
    elif status == "known":
        if "value" not in entry:
            raise ValidationError(f"{path}.value: required for known status")
        if not entry["evidence_refs"]:
            raise ValidationError(f"{path}.evidence_refs: known entries require evidence")
        if "unknown_reason" in entry:
            raise ValidationError(f"{path}.unknown_reason: invalid for known status")
        _reject_placeholder_known_values(entry["value"], f"{path}.value")
    else:
        if "rationale" not in entry:
            raise ValidationError(f"{path}.rationale: required for not_applicable status")
        _expect_type(entry["rationale"], str, f"{path}.rationale")
        if "value" in entry:
            raise ValidationError(f"{path}.value: not_applicable entries must not carry values")

    _validate_known_pin_assignment(entry, path)
    return entry_id


def validate_document(document: Any) -> None:
    _expect_type(document, dict, "$")
    allowed_keys = {
        "schema_version",
        "document_id",
        "description",
        "required_unknowns",
        "unknown_blocker_summary",
        "live_action_gates",
        "procedure_proposals",
        "entries",
    }
    extra = sorted(set(document) - allowed_keys)
    if extra:
        raise ValidationError(f"$: unknown key(s): {', '.join(extra)}")
    _require_keys(
        document,
        {"schema_version", "document_id", "description", "required_unknowns", "entries"},
        "$",
    )

    if document["schema_version"] != SCHEMA_VERSION:
        raise ValidationError(
            f"$.schema_version: expected {SCHEMA_VERSION!r}, got {document['schema_version']!r}"
        )
    for key in ("document_id", "description"):
        _expect_type(document[key], str, f"$.{key}")
        if not document[key]:
            raise ValidationError(f"$.{key}: must not be empty")

    _validate_string_list(document["required_unknowns"], "$.required_unknowns")
    _expect_type(document["entries"], list, "$.entries")
    if not document["entries"]:
        raise ValidationError("$.entries: must not be empty")

    entries_by_id: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(document["entries"]):
        entry_id = _validate_entry(entry, f"$.entries[{index}]")
        if entry_id in entries_by_id:
            raise ValidationError(f"$.entries[{index}].id: duplicate id {entry_id!r}")
        entries_by_id[entry_id] = entry

    for entry_id in document["required_unknowns"]:
        entry = entries_by_id.get(entry_id)
        if entry is None:
            raise ValidationError(f"$.required_unknowns: missing entry {entry_id!r}")
        if entry["status"] != "unknown":
            raise ValidationError(
                f"$.required_unknowns: {entry_id!r} must remain status 'unknown'"
            )

    if "unknown_blocker_summary" in document:
        _validate_blocker_summary(
            document["unknown_blocker_summary"], entries_by_id, "$.unknown_blocker_summary"
        )
    if "live_action_gates" in document:
        _validate_live_action_gates(
            document["live_action_gates"], entries_by_id, "$.live_action_gates"
        )
    if "procedure_proposals" in document:
        _validate_procedure_proposals(
            document["procedure_proposals"], "$.procedure_proposals"
        )


def validate_file(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        validate_document(json.load(handle))


def load_document(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _default_paths() -> list[Path]:
    evidence_dir = Path(__file__).resolve().parents[1] / "evidence"
    return sorted(evidence_dir.glob("*.example.json"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Evidence status JSON files to validate. Defaults to evidence/*.example.json.",
    )
    parser.add_argument(
        "--emit-telemetry-jsonl",
        action="store_true",
        help=(
            "After validating evidence files, emit the offline software-only "
            "telemetry projection as JSONL to stdout."
        ),
    )
    args = parser.parse_args(argv)

    paths = args.paths or _default_paths()
    if not paths:
        print("No evidence status files found.", file=sys.stderr)
        return 1

    failed = False
    for path in paths:
        try:
            document = load_document(path)
            validate_document(document)
            if args.emit_telemetry_jsonl:
                records = project_evidence_to_telemetry_records(document)
                validate_telemetry_records(records)
                for record in records:
                    print(json.dumps(record, sort_keys=True, separators=(",", ":")))
        except (
            OSError,
            json.JSONDecodeError,
            ValidationError,
            TelemetryProjectionError,
        ) as exc:
            print(f"{path}: FAIL: {exc}", file=sys.stderr)
            failed = True
        else:
            if not args.emit_telemetry_jsonl:
                print(f"{path}: OK")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
