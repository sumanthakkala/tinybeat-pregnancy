"""checklist_add_question — add one question to the live prep checklist (PRD-15).

Each call writes a row + fires byo.db.changed, so the checklist visibly grows in
the UI as the agent works. Creates the checklist on the first question; refuses
once it's finalized (locked).
"""

from __future__ import annotations

import json
import secrets
from typing import Any

from sqlalchemy import func, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from tinybeat_pregnancy.storage.models.checklist_question import ChecklistQuestion
from byoh_bridge.workflows import Tool
from .._serialize import get_or_create_checklist

SCHEMA: dict = {
    "name": "checklist_add_question",
    "description": (
        "Add one question the user should raise with their provider at this visit. "
        "Frame it as something to ASK (never medical advice). Include why_it_matters "
        "(a short, plain reason). idempotency_key 'checklist:<appointment_id>:q<index>'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "appointment_id": {"type": "string"},
            "question_text": {"type": "string"},
            "why_it_matters": {"type": "string"},
            "idempotency_key": {"type": "string"},
        },
        "required": ["appointment_id", "question_text", "idempotency_key"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    appt_id = str(args.get("appointment_id", "")).strip()
    text = str(args.get("question_text", "")).strip()
    key = str(args.get("idempotency_key", "")).strip()
    why = args.get("why_it_matters")
    if not appt_id or not text or not key:
        return json.dumps({"ok": False, "error": "appointment_id, question_text and idempotency_key required"})

    with storage.session() as s:
        if s.get(Appointment, appt_id) is None:
            return json.dumps({"ok": False, "error": "unknown appointment"})
        ckl = get_or_create_checklist(s, appt_id)
        if ckl.finalized:
            return json.dumps({"ok": False, "error": "checklist is finalized; start a new session to amend"})
        existing = s.scalar(select(ChecklistQuestion).where(ChecklistQuestion.idempotency_key == key))
        if existing is not None:
            return json.dumps({"ok": True, "id": existing.id, "deduped": True})
        count = s.scalar(
            select(func.count()).select_from(ChecklistQuestion).where(ChecklistQuestion.appointment_id == appt_id)
        ) or 0
        row = ChecklistQuestion(
            id="clq_" + secrets.token_hex(8),
            appointment_id=appt_id,
            question_text=text,
            why_it_matters=(str(why) if why else None),
            sort_index=int(count),
            idempotency_key=key,
        )
        s.add(row)
        s.flush()
        row_id = row.id
    return json.dumps({"ok": True, "id": row_id})


TOOL = Tool(
    name="checklist_add_question",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Add one question to the appointment-prep checklist.",
    emoji="❓",
)
