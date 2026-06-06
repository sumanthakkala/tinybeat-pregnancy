"""byo.symptoms.frequency — counts per symptom for the frequency view (PRD-12)."""

from __future__ import annotations

from sqlalchemy import func, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.symptom_log import SymptomLog
from byoh_bridge.workflows import Rpc
from .._taxonomy import is_red_flag, label_of


def handler(_params: dict) -> dict:
    """Return ``{counts: [{symptom, label, red_flag, n}]}`` (most frequent first)."""
    with storage.session() as s:
        rows = s.execute(
            select(SymptomLog.symptom, func.count()).group_by(SymptomLog.symptom)
        ).all()

    counts = [
        {"symptom": sym, "label": label_of(sym), "red_flag": is_red_flag(sym), "n": int(n)}
        for sym, n in rows
    ]
    counts.sort(key=lambda c: (-c["n"], c["label"]))
    return {"counts": counts}


RPC = Rpc(
    method="byo.symptoms.frequency",
    handler=handler,
    description="Count of occurrences per symptom (most frequent first).",
    read_only=True,
)
