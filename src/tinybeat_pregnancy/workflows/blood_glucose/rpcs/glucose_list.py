"""byo.glucose.list — recent glucose readings for the dashboard (PRD-11).

The FE filters by reading_type and computes per-type trends from this single
list (so a separate byo.glucose.trends RPC isn't needed at v1 volumes).
"""

from __future__ import annotations

from typing import Any

from tinybeat_pregnancy.storage.models.glucose_reading import GlucoseReading
from byoh_bridge.workflows import make_list_rpc


def _serialize(r: Any) -> dict:
    return {
        "id": r.id,
        "recorded_at": r.recorded_at,
        "value": r.value,
        "unit": r.unit,
        "reading_type": r.reading_type,
        "meal": r.meal,
        "note": r.note,
        "source": r.source,
        "source_report_id": r.source_report_id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


RPC = make_list_rpc(
    method="byo.glucose.list",
    model=GlucoseReading,
    serialize=_serialize,
    description="Return the most recent N glucose readings.",
)
