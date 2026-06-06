"""byo.checklist.list_for_appt{appointment_id} — the live checklist pane (PRD-15)."""

from __future__ import annotations

from sqlalchemy import asc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.checklist_question import ChecklistQuestion
from byoh_bridge.workflows import Rpc
from .._serialize import question_to_dict


def handler(params: dict) -> dict:
    appt_id = str(params.get("appointment_id") or "")
    with storage.session() as s:
        rows = (
            s.execute(
                select(ChecklistQuestion)
                .where(ChecklistQuestion.appointment_id == appt_id)
                .order_by(asc(ChecklistQuestion.sort_index), asc(ChecklistQuestion.created_at))
            )
            .scalars()
            .all()
        )
        questions = [question_to_dict(q) for q in rows]
    return {"questions": questions, "count": len(questions)}


RPC = Rpc(
    method="byo.checklist.list_for_appt",
    handler=handler,
    description="Checklist questions for an appointment (live-building pane).",
    read_only=True,
)
