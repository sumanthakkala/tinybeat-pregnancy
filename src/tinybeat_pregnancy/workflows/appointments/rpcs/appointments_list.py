"""byo.appointments.list{range?} — calendar/timeline data (PRD-14).

range: "upcoming" (scheduled, soonest first) · "past" (everything else, newest
first) · "all" (newest first). starts_at is ISO TEXT, compared on its minute
prefix so a mix of `…T14:00` / `…T14:00:00` sorts consistently.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from byoh_bridge.workflows import Rpc
from .._serialize import appointment_to_dict


def handler(params: dict) -> dict:
    rng = str(params.get("range") or "all")
    limit = int(params.get("limit", 300) or 300)
    now16 = datetime.now().isoformat()[:16]

    with storage.session() as s:
        rows = s.execute(select(Appointment)).scalars().all()

    def upcoming(a) -> bool:
        return a.status == "scheduled" and a.starts_at[:16] >= now16

    if rng == "upcoming":
        rows = sorted((a for a in rows if upcoming(a)), key=lambda a: a.starts_at)
    elif rng == "past":
        rows = sorted((a for a in rows if not upcoming(a)), key=lambda a: a.starts_at, reverse=True)
    else:
        rows = sorted(rows, key=lambda a: a.starts_at, reverse=True)

    payload = [appointment_to_dict(a) for a in rows[:limit]]
    return {"rows": payload, "count": len(payload)}


RPC = Rpc(
    method="byo.appointments.list",
    handler=handler,
    description="List appointments (range: upcoming | past | all).",
    read_only=True,
)
