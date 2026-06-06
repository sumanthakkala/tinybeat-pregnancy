"""byo.appointments.get{appointment_id} — detail view (PRD-14).

Returns the appointment + its follow-up notes. The checklist/questions/debrief
slots are stubbed null until PRD-15/19 land (they join on appointment_id).
"""

from __future__ import annotations

from sqlalchemy import asc, func, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from tinybeat_pregnancy.storage.models.appointment_checklist import AppointmentChecklist
from tinybeat_pregnancy.storage.models.appointment_followup import AppointmentFollowup
from tinybeat_pregnancy.storage.models.checklist_question import ChecklistQuestion
from byoh_bridge.workflows import Rpc
from .._serialize import appointment_to_dict, followup_to_dict


def handler(params: dict) -> dict:
    appt_id = str(params.get("appointment_id") or "")
    with storage.session() as s:
        a = s.get(Appointment, appt_id) if appt_id else None
        if a is None:
            return {"row": None}
        followups = (
            s.execute(
                select(AppointmentFollowup)
                .where(AppointmentFollowup.appointment_id == appt_id)
                .order_by(asc(AppointmentFollowup.created_at))
            )
            .scalars()
            .all()
        )
        # Checklist summary (PRD-15) — the detail view's Prep tab uses this.
        ckl = s.query(AppointmentChecklist).filter(AppointmentChecklist.appointment_id == appt_id).one_or_none()
        q_count = s.scalar(
            select(func.count()).select_from(ChecklistQuestion).where(ChecklistQuestion.appointment_id == appt_id)
        ) or 0
        checklist = {"exists": ckl is not None, "finalized": bool(ckl.finalized) if ckl else False, "question_count": int(q_count)}
        return {
            "row": appointment_to_dict(a),
            "followups": [followup_to_dict(f) for f in followups],
            "checklist": checklist,
            "questions": None,  # PRD-19
            "debrief": None,  # PRD-19
        }


RPC = Rpc(
    method="byo.appointments.get",
    handler=handler,
    description="One appointment with its follow-up notes (+ checklist/questions/debrief as they land).",
    read_only=True,
)
