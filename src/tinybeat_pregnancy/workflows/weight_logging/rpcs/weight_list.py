"""byo.weight.list — fetch the most recent N weight rows for the UI.

One RPC, one file. The handler uses the ORM to query and returns plain
dicts the UI can render directly.
"""

from __future__ import annotations

from sqlalchemy import desc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.weight_log import WeightLog
from byoh_bridge.workflows import Rpc


def handler(params: dict) -> dict:
    """Return the most recent ``limit`` rows from ``weight_logs``.

    Params:
        limit (int, optional): max rows to return. Default 50.

    Result:
        {"rows": list[dict], "count": int}
    """
    limit = int(params.get("limit", 50) or 50)

    with storage.session() as s:
        rows = s.execute(
            select(WeightLog)
            .order_by(desc(WeightLog.recorded_at), desc(WeightLog.id))
            .limit(limit)
        ).scalars().all()

        # Convert ORM objects to plain dicts the UI's WeightLogsPanel
        # expects. created_at is a datetime; isoformat it for JSON.
        payload = [
            {
                "id": r.id,
                "recorded_at": r.recorded_at,
                "kg": r.kg,
                "note": r.note,
                "source": r.source,
                "source_report_id": r.source_report_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]

    return {"rows": payload, "count": len(payload)}


RPC = Rpc(
    method="byo.weight.list",
    handler=handler,
    description="Return the most recent N weight rows.",
    read_only=True,
)
