"""appointment_update — edit or cancel an appointment (PRD-14).

Setting fields to given values is naturally idempotent (re-applying the same
update is a no-op), so no dedup table is needed. Cancel = status="cancelled".
"""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from byoh_bridge.workflows import Tool

_STATUSES = {"scheduled", "done", "cancelled"}

SCHEMA: dict = {
    "name": "appointment_update",
    "description": (
        "Edit an existing appointment (reschedule, change provider/location/notes, "
        "or mark it done/cancelled). Only pass the fields that change. To cancel, "
        "set status='cancelled'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "appointment_id": {"type": "string"},
            "starts_at": {"type": "string", "description": "New ISO datetime (optional)."},
            "kind": {"type": "string"},
            "provider": {"type": "string"},
            "location": {"type": "string"},
            "notes": {"type": "string"},
            "status": {"type": "string", "enum": sorted(_STATUSES)},
            "idempotency_key": {"type": "string"},
        },
        "required": ["appointment_id", "idempotency_key"],
        "additionalProperties": False,
    },
}

_FIELDS = ("starts_at", "kind", "provider", "location", "notes", "status")


def handler(args: dict[str, Any], **_: Any) -> str:
    appt_id = str(args.get("appointment_id", "")).strip()
    if not appt_id:
        return json.dumps({"ok": False, "error": "appointment_id required"})
    status = args.get("status")
    if status is not None and status not in _STATUSES:
        return json.dumps({"ok": False, "error": f"status must be one of {sorted(_STATUSES)}"})

    with storage.session() as s:
        a = s.get(Appointment, appt_id)
        if a is None:
            return json.dumps({"ok": False, "error": "unknown appointment"})
        for f in _FIELDS:
            v = args.get(f)
            if v is not None:
                setattr(a, f, v)
        s.flush()
        out = {"ok": True, "id": a.id, "status": a.status}
    return json.dumps(out)


TOOL = Tool(
    name="appointment_update",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Edit or cancel an appointment.",
    emoji="✏️",
)
