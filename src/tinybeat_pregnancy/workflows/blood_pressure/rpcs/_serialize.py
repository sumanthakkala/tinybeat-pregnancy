"""BpReading → plain dict, shared by byo.bp.list + byo.bp.latest."""

from __future__ import annotations

from typing import Any


def bp_to_dict(r: Any) -> dict:
    return {
        "id": r.id,
        "recorded_at": r.recorded_at,
        "systolic": r.systolic,
        "diastolic": r.diastolic,
        "pulse": r.pulse,
        "arm": r.arm,
        "position": r.position,
        "note": r.note,
        "source": r.source,
        "source_report_id": r.source_report_id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
