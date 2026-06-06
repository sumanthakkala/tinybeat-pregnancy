"""Checklist helpers — get-or-create + serialize (shared by tools + RPCs)."""

from __future__ import annotations

import secrets
from typing import Any

from tinybeat_pregnancy.storage.models.appointment_checklist import AppointmentChecklist


def get_or_create_checklist(s, appointment_id: str) -> AppointmentChecklist:
    """One checklist per appointment; create on first write."""
    obj = (
        s.query(AppointmentChecklist)
        .filter(AppointmentChecklist.appointment_id == appointment_id)
        .one_or_none()
    )
    if obj is None:
        obj = AppointmentChecklist(id="ckl_" + secrets.token_hex(8), appointment_id=appointment_id, finalized=False)
        s.add(obj)
        s.flush()
    return obj


def question_to_dict(q: Any) -> dict:
    return {
        "id": q.id,
        "appointment_id": q.appointment_id,
        "question_text": q.question_text,
        "why_it_matters": q.why_it_matters,
        "answer_text": q.answer_text,
        "sort_index": q.sort_index,
        "created_at": q.created_at.isoformat() if q.created_at else None,
    }
