"""ChecklistQuestion ORM model — one question to raise at a visit (PRD-15)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class ChecklistQuestion(Base):
    __tablename__ = "checklist_questions"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # "clq_…"
    appointment_id: Mapped[str] = mapped_column(
        String, ForeignKey("appointments.id"), nullable=False, index=True,
    )
    question_text: Mapped[str] = mapped_column(String, nullable=False)
    why_it_matters: Mapped[str | None] = mapped_column(String, nullable=True)
    answer_text: Mapped[str | None] = mapped_column(String, nullable=True)  # ticked off at the visit
    sort_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChecklistQuestion {self.id} appt={self.appointment_id}>"
