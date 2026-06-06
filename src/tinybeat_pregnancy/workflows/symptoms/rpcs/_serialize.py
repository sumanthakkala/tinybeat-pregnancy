"""SymptomLog → plain dict (shared by the symptom RPCs)."""

from __future__ import annotations

from typing import Any

from .._taxonomy import is_red_flag, label_of


def symptom_to_dict(r: Any) -> dict:
    return {
        "id": r.id,
        "recorded_at": r.recorded_at,
        "symptom": r.symptom,
        "label": label_of(r.symptom),
        "red_flag": is_red_flag(r.symptom),
        "severity": r.severity,
        "note": r.note,
        "source": r.source,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
