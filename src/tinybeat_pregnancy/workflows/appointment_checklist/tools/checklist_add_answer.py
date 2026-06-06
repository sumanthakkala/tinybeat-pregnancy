"""checklist_add_answer — record the answer to a checklist question (PRD-15).

Used to capture what the provider said against a question (also tickable in the
UI). Setting the answer is naturally idempotent.
"""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.checklist_question import ChecklistQuestion
from byoh_bridge.workflows import Tool

SCHEMA: dict = {
    "name": "checklist_add_answer",
    "description": "Record an answer/note against a checklist question (e.g. what the provider said).",
    "parameters": {
        "type": "object",
        "properties": {
            "appointment_id": {"type": "string"},
            "question_id": {"type": "string"},
            "answer_text": {"type": "string"},
            "idempotency_key": {"type": "string"},
        },
        "required": ["appointment_id", "question_id", "answer_text", "idempotency_key"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    appt_id = str(args.get("appointment_id", "")).strip()
    qid = str(args.get("question_id", "")).strip()
    answer = str(args.get("answer_text", "")).strip()
    if not qid or not answer:
        return json.dumps({"ok": False, "error": "question_id and answer_text required"})
    with storage.session() as s:
        q = s.get(ChecklistQuestion, qid)
        if q is None or (appt_id and q.appointment_id != appt_id):
            return json.dumps({"ok": False, "error": "unknown question"})
        q.answer_text = answer
        s.flush()
    return json.dumps({"ok": True, "id": qid})


TOOL = Tool(
    name="checklist_add_answer",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Record an answer against a checklist question.",
    emoji="✍️",
)
