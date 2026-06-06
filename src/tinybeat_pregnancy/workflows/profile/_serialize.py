"""Profile → plain dict, shared by the RPCs and the agent-read tool."""

from __future__ import annotations

from typing import Any


def profile_to_dict(p: Any) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "due_date": p.due_date,
        "lmp_date": p.lmp_date,
        "edd_source": p.edd_source,
        "prepreg_weight_kg": p.prepreg_weight_kg,
        "height_cm": p.height_cm,
        "units_weight": p.units_weight,
        "units_length": p.units_length,
        "emergency_contact_name": p.emergency_contact_name,
        "emergency_contact_phone": p.emergency_contact_phone,
        "postpartum": bool(p.postpartum),
        "birth_date": p.birth_date,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
