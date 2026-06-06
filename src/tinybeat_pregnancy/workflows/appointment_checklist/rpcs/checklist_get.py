"""byo.checklist.get{appointment_id} — the finalized checklist + lock state (PRD-15)."""

from __future__ import annotations

from sqlalchemy import asc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment_checklist import AppointmentChecklist
from tinybeat_pregnancy.storage.models.checklist_question import ChecklistQuestion
from byoh_bridge.workflows import Rpc
from .._serialize import question_to_dict


def handler(params: dict) -> dict:
    appt_id = str(params.get("appointment_id") or "")
    with storage.session() as s:
        ckl = (
            s.query(AppointmentChecklist).filter(AppointmentChecklist.appointment_id == appt_id).one_or_none()
        )
        rows = (
            s.execute(
                select(ChecklistQuestion)
                .where(ChecklistQuestion.appointment_id == appt_id)
                .order_by(asc(ChecklistQuestion.sort_index), asc(ChecklistQuestion.created_at))
            )
            .scalars()
            .all()
        )
        return {
            "appointment_id": appt_id,
            "exists": ckl is not None,
            "finalized": bool(ckl.finalized) if ckl else False,
            "questions": [question_to_dict(q) for q in rows],
        }


RPC = Rpc(
    method="byo.checklist.get",
    handler=handler,
    description="Get an appointment's checklist (questions + finalized flag).",
    read_only=True,
)
