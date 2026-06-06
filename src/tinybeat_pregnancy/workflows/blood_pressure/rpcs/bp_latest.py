"""byo.bp.latest — the most recent BP reading (PRD-10), for at-a-glance cards."""

from __future__ import annotations

from sqlalchemy import desc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.bp_reading import BpReading
from byoh_bridge.workflows import Rpc
from ._serialize import bp_to_dict


def handler(_params: dict) -> dict:
    with storage.session() as s:
        row = s.execute(
            select(BpReading).order_by(desc(BpReading.recorded_at), desc(BpReading.id)).limit(1)
        ).scalar_one_or_none()
        return {"row": bp_to_dict(row) if row else None}


RPC = Rpc(
    method="byo.bp.latest",
    handler=handler,
    description="Return the single most recent BP reading (or null).",
    read_only=True,
)
