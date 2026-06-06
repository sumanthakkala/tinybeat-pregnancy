"""checklist_finalize — lock the prep checklist (PRD-15).

Sets ``finalized=True``; further changes require a new session (by design).
"""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from byoh_bridge.workflows import Tool
from .._serialize import get_or_create_checklist

SCHEMA: dict = {
    "name": "checklist_finalize",
    "description": "Lock the appointment-prep checklist when the user is done. idempotency_key 'checklist:<appointment_id>:finalize'.",
    "parameters": {
        "type": "object",
        "properties": {
            "appointment_id": {"type": "string"},
            "idempotency_key": {"type": "string"},
        },
        "required": ["appointment_id", "idempotency_key"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    appt_id = str(args.get("appointment_id", "")).strip()
    if not appt_id:
        return json.dumps({"ok": False, "error": "appointment_id required"})
    with storage.session() as s:
        if s.get(Appointment, appt_id) is None:
            return json.dumps({"ok": False, "error": "unknown appointment"})
        ckl = get_or_create_checklist(s, appt_id)
        ckl.finalized = True
        s.flush()
    return json.dumps({"ok": True, "appointment_id": appt_id, "finalized": True})


TOOL = Tool(
    name="checklist_finalize",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Lock the appointment-prep checklist.",
    emoji="🔒",
)
