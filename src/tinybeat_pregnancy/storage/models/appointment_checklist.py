"""AppointmentChecklist ORM model — one prep checklist per appointment (PRD-15).

The guided-conversation artifact: the agent builds it live (one
``checklist_questions`` row per agreed item), then ``finalize`` locks it. One
checklist per appointment (the FK is UNIQUE).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class AppointmentChecklist(Base):
    __tablename__ = "appointment_checklists"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # "ckl_…"
    appointment_id: Mapped[str] = mapped_column(
        String, ForeignKey("appointments.id"), nullable=False, unique=True,
    )
    finalized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AppointmentChecklist {self.id} appt={self.appointment_id} finalized={self.finalized}>"
