"""Appointment / followup → plain dicts (shared by tools + RPCs)."""

from __future__ import annotations

from typing import Any


def appointment_to_dict(a: Any) -> dict:
    return {
        "id": a.id,
        "starts_at": a.starts_at,
        "kind": a.kind,
        "provider": a.provider,
        "location": a.location,
        "notes": a.notes,
        "status": a.status,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def followup_to_dict(f: Any) -> dict:
    return {
        "id": f.id,
        "appointment_id": f.appointment_id,
        "note": f.note,
        "created_at": f.created_at.isoformat() if f.created_at else None,
    }
