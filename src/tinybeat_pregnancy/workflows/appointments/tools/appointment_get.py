"""appointment_get — read one appointment + its notes (PRD-14).

A *tool* (not just an RPC) because the checklist agent (PRD-15) needs to read an
appointment's context inside its own scoped session.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import asc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from tinybeat_pregnancy.storage.models.appointment_followup import AppointmentFollowup
from byoh_bridge.workflows import Tool
from .._serialize import appointment_to_dict, followup_to_dict

SCHEMA: dict = {
    "name": "appointment_get",
    "description": "Get one appointment (with its follow-up notes) by id.",
    "parameters": {
        "type": "object",
        "properties": {"appointment_id": {"type": "string"}},
        "required": ["appointment_id"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    appt_id = str(args.get("appointment_id", "")).strip()
    if not appt_id:
        return json.dumps({"ok": False, "error": "appointment_id required"})
    with storage.session() as s:
        a = s.get(Appointment, appt_id)
        if a is None:
            return json.dumps({"ok": False, "error": "unknown appointment"})
        followups = (
            s.execute(
                select(AppointmentFollowup)
                .where(AppointmentFollowup.appointment_id == appt_id)
                .order_by(asc(AppointmentFollowup.created_at))
            )
            .scalars()
            .all()
        )
        out = {"ok": True, "appointment": appointment_to_dict(a), "followups": [followup_to_dict(f) for f in followups]}
    return json.dumps(out)


TOOL = Tool(
    name="appointment_get",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Get one appointment with its follow-up notes.",
    emoji="🔎",
)
