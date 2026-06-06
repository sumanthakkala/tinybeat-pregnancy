"""byo.symptoms.calendar — per-day rollup for the heatmap (PRD-12)."""

from __future__ import annotations

from sqlalchemy import select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.symptom_log import SymptomLog
from byoh_bridge.workflows import Rpc


def handler(_params: dict) -> dict:
    """Return ``{days: [{date, count, maxSeverity, symptoms[]}]}`` (date-sorted)."""
    with storage.session() as s:
        rows = s.execute(
            select(SymptomLog.recorded_at, SymptomLog.symptom, SymptomLog.severity)
        ).all()

    by_date: dict[str, dict] = {}
    for recorded_at, symptom, severity in rows:
        day = str(recorded_at)[:10]
        e = by_date.setdefault(day, {"date": day, "count": 0, "maxSeverity": 0, "symptoms": []})
        e["count"] += 1
        if severity:
            e["maxSeverity"] = max(e["maxSeverity"], int(severity))
        if symptom not in e["symptoms"]:
            e["symptoms"].append(symptom)

    return {"days": sorted(by_date.values(), key=lambda x: x["date"])}


RPC = Rpc(
    method="byo.symptoms.calendar",
    handler=handler,
    description="Per-day symptom rollup (count, max severity, symptom keys) for the heatmap.",
    read_only=True,
)
