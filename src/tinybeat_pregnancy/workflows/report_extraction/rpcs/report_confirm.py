"""byo.report.confirm{value_id, edits?} — the human-tap that makes a value official.

This is a **write RPC** (a user action, not an agent decision — like the PRD-03
profile RPC). It writes the staged value into its real metric table with
``source="report"`` provenance, stamps ``confirmed_at`` (audit), and records where
it landed. Idempotent on the value: a second confirm is a no-op.
"""

from __future__ import annotations

import json
from datetime import date, datetime

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.extracted_value import ExtractedValue
from tinybeat_pregnancy.storage.models.profile import Profile
from byoh_bridge.workflows import Rpc
from .._metrics import TABLE_METRICS, validate, write_metric_row


def handler(params: dict) -> dict:
    value_id = str(params.get("value_id") or "")
    edits = params.get("edits") or {}
    if not value_id:
        return {"ok": False, "error": "value_id required"}

    with storage.session() as s:
        ev = s.get(ExtractedValue, value_id)
        if ev is None:
            return {"ok": False, "error": "unknown value"}
        if ev.status == "confirmed":
            return {"ok": True, "already": True, "target_table": ev.target_row_table, "target_row_id": ev.target_row_id}

        value = json.loads(ev.value_json)
        if isinstance(edits.get("value"), dict):
            value = {**value, **edits["value"]}
        when = str(edits.get("date") or ev.date or date.today().isoformat())[:10]

        verr = validate(ev.metric, value)
        if verr:
            return {"ok": False, "error": f"edited value invalid: {verr}"}

        target_table = None
        target_row_id = None
        if ev.metric in TABLE_METRICS:
            result = write_metric_row(s, ev.metric, value, when, ev.document_id, f"report:{ev.id}")
            if result:
                target_table, target_row_id = result
        elif ev.metric == "edd" and value.get("date"):
            p = s.get(Profile, 1)
            if p is None:
                p = Profile(id=1, units_weight="kg", units_length="cm")
                s.add(p)
            p.due_date = str(value["date"])[:10]
            p.edd_source = "ultrasound"
            target_table, target_row_id = "profile", 1
        # else (hemoglobin/hcg/tsh/blood_type/fundal_height/other): no chart yet —
        # it stays staged-confirmed for the records library (PRD-42).

        ev.status = "confirmed"
        ev.target_row_table = target_table
        ev.target_row_id = target_row_id
        ev.confirmed_at = datetime.now()
        s.flush()
        out = {"ok": True, "metric": ev.metric, "target_table": target_table, "target_row_id": target_row_id}
    return out


RPC = Rpc(
    method="byo.report.confirm",
    handler=handler,
    description="Confirm a staged extracted value → write it to its metric table with provenance.",
    read_only=False,
)
