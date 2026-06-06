"""byo.appointments.next — the soonest upcoming scheduled visit (PRD-14).

Powers the "Next appointment" hero card and the Today snippet.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import asc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from byoh_bridge.workflows import Rpc
from .._serialize import appointment_to_dict


def handler(_params: dict) -> dict:
    now16 = datetime.now().isoformat()[:16]
    with storage.session() as s:
        rows = (
            s.execute(
                select(Appointment).where(Appointment.status == "scheduled").order_by(asc(Appointment.starts_at))
            )
            .scalars()
            .all()
        )
    upcoming = next((a for a in rows if a.starts_at[:16] >= now16), None)
    return {"row": appointment_to_dict(upcoming) if upcoming else None}


RPC = Rpc(
    method="byo.appointments.next",
    handler=handler,
    description="The soonest upcoming scheduled appointment (or null).",
    read_only=True,
)
