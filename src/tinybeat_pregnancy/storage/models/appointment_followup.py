"""AppointmentFollowup ORM model — a note attached to an appointment (PRD-14)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class AppointmentFollowup(Base):
    __tablename__ = "appointment_followups"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # "af_…"
    appointment_id: Mapped[str] = mapped_column(
        String, ForeignKey("appointments.id"), nullable=False, index=True,
    )
    note: Mapped[str] = mapped_column(String, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AppointmentFollowup {self.id} appt={self.appointment_id}>"
