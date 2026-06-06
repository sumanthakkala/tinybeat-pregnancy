"""appointment_add_followup_note — attach a note to an appointment (PRD-14)."""

from __future__ import annotations

import json
import secrets
from typing import Any

from sqlalchemy import select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from tinybeat_pregnancy.storage.models.appointment_followup import AppointmentFollowup
from byoh_bridge.workflows import Tool

SCHEMA: dict = {
    "name": "appointment_add_followup_note",
    "description": "Attach a follow-up note to an appointment (e.g. what the provider said).",
    "parameters": {
        "type": "object",
        "properties": {
            "appointment_id": {"type": "string"},
            "note": {"type": "string"},
            "idempotency_key": {"type": "string", "description": "Stable key 'appt:note:<id>:<n>'."},
        },
        "required": ["appointment_id", "note", "idempotency_key"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    appt_id = str(args.get("appointment_id", "")).strip()
    note = str(args.get("note", "")).strip()
    key = str(args.get("idempotency_key", "")).strip()
    if not appt_id or not note or not key:
        return json.dumps({"ok": False, "error": "appointment_id, note and idempotency_key required"})

    with storage.session() as s:
        if s.get(Appointment, appt_id) is None:
            return json.dumps({"ok": False, "error": "unknown appointment"})
        existing = s.scalar(select(AppointmentFollowup).where(AppointmentFollowup.idempotency_key == key))
        if existing is not None:
            return json.dumps({"ok": True, "id": existing.id, "deduped": True})
        row = AppointmentFollowup(
            id="af_" + secrets.token_hex(8), appointment_id=appt_id, note=note, idempotency_key=key,
        )
        s.add(row)
        s.flush()
        row_id = row.id
    return json.dumps({"ok": True, "id": row_id})


TOOL = Tool(
    name="appointment_add_followup_note",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Attach a follow-up note to an appointment.",
    emoji="🗒️",
)
