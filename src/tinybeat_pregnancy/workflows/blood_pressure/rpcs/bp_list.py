"""byo.bp.list — recent BP readings for the RangeChart (PRD-10)."""

from __future__ import annotations

from tinybeat_pregnancy.storage.models.bp_reading import BpReading
from byoh_bridge.workflows import make_list_rpc
from ._serialize import bp_to_dict

RPC = make_list_rpc(
    method="byo.bp.list",
    model=BpReading,
    serialize=bp_to_dict,
    description="Return the most recent N blood-pressure readings.",
)
