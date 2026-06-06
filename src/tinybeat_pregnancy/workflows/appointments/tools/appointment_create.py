"""appointment_create — schedule one care visit (PRD-14)."""

from __future__ import annotations

import json
import secrets
from typing import Any

from sqlalchemy import select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from byoh_bridge.workflows import Tool

SCHEMA: dict = {
    "name": "appointment_create",
    "description": (
        "Schedule one appointment. Parse the user's natural language ('OB visit "
        "next Tuesday at 2pm with Dr. Lee'), resolve relative dates against today, "
        "and confirm the date/time back to the user. Never invent a provider or "
        "location the user didn't give. idempotency_key 'appt:<starts_at>:<kind>'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "starts_at": {"type": "string", "description": "ISO datetime, e.g. 2026-06-10T14:00."},
            "kind": {"type": "string", "description": "Visit type, e.g. 'OB visit', 'anatomy scan', 'glucose screen'."},
            "provider": {"type": "string", "description": "Who they're seeing (optional)."},
            "location": {"type": "string", "description": "Where (optional)."},
            "notes": {"type": "string", "description": "Anything to remember (optional)."},
            "idempotency_key": {"type": "string", "description": "Stable de-dupe key. Required."},
        },
        "required": ["starts_at", "kind", "idempotency_key"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    starts_at = str(args.get("starts_at", "")).strip()
    kind = str(args.get("kind", "")).strip()
    key = str(args.get("idempotency_key", "")).strip()
    if not starts_at or not kind or not key:
        return json.dumps({"ok": False, "error": "starts_at, kind and idempotency_key required"})

    with storage.session() as s:
        existing = s.scalar(select(Appointment).where(Appointment.idempotency_key == key))
        if existing is not None:
            return json.dumps({"ok": True, "id": existing.id, "deduped": True})
        row = Appointment(
            id="appt_" + secrets.token_hex(8),
            starts_at=starts_at,
            kind=kind,
            provider=(str(args.get("provider")) if args.get("provider") else None),
            location=(str(args.get("location")) if args.get("location") else None),
            notes=(str(args.get("notes")) if args.get("notes") else None),
            status="scheduled",
            idempotency_key=key,
        )
        s.add(row)
        s.flush()
        appt_id = row.id
    return json.dumps({"ok": True, "id": appt_id, "starts_at": starts_at, "kind": kind})


TOOL = Tool(
    name="appointment_create",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Schedule one care appointment.",
    emoji="📅",
)
