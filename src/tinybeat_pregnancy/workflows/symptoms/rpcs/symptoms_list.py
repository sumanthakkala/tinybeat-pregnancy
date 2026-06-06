"""byo.symptoms.list — recent symptom rows (optional tag filter)."""

from __future__ import annotations

from sqlalchemy import desc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.symptom_log import SymptomLog
from byoh_bridge.workflows import Rpc
from ._serialize import symptom_to_dict


def handler(params: dict) -> dict:
    limit = int(params.get("limit", 300) or 300)
    symptom = params.get("symptom")
    with storage.session() as s:
        q = select(SymptomLog).order_by(desc(SymptomLog.recorded_at), desc(SymptomLog.id)).limit(limit)
        if symptom:
            q = q.where(SymptomLog.symptom == symptom)
        rows = s.execute(q).scalars().all()
        payload = [symptom_to_dict(r) for r in rows]
    return {"rows": payload, "count": len(payload)}


RPC = Rpc(
    method="byo.symptoms.list",
    handler=handler,
    description="Recent symptom rows (optional `symptom` tag filter).",
    read_only=True,
)
