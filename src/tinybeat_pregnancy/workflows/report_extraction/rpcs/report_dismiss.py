"""byo.report.dismiss{value_id} — the user declines a staged value (PRD-13).

Marks it ``dismissed`` so nothing leaks into the metrics. Idempotent.
"""

from __future__ import annotations

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.extracted_value import ExtractedValue
from byoh_bridge.workflows import Rpc


def handler(params: dict) -> dict:
    value_id = str(params.get("value_id") or "")
    if not value_id:
        return {"ok": False, "error": "value_id required"}
    with storage.session() as s:
        ev = s.get(ExtractedValue, value_id)
        if ev is None:
            return {"ok": False, "error": "unknown value"}
        if ev.status == "proposed":
            ev.status = "dismissed"
        return {"ok": True, "status": ev.status}


RPC = Rpc(
    method="byo.report.dismiss",
    handler=handler,
    description="Dismiss a staged extracted value (it never reaches the metrics).",
    read_only=False,
)
