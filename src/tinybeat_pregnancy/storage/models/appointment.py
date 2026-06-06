"""Appointment ORM model — one care visit (PRD-14).

The logistics anchor the prep-checklist (PRD-15), questions/debrief (PRD-19), and
test-window (PRD-20) features hang off (via ``appointment_id`` FKs). ``starts_at``
is stored as TEXT ISO so it sorts and compares lexicographically.

After editing, autogenerate a migration from the plugin dir:
    ~/.hermes/hermes-agent/venv/bin/alembic revision --autogenerate -m "..."
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # "appt_…"
    starts_at: Mapped[str] = mapped_column(String, nullable=False, index=True)  # ISO datetime
    kind: Mapped[str] = mapped_column(String, nullable=False)  # "OB visit", "anatomy scan", …
    provider: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    # scheduled | done | cancelled
    status: Mapped[str] = mapped_column(String, nullable=False, default="scheduled", server_default="scheduled")

    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Appointment {self.id} {self.kind!r} {self.starts_at} {self.status}>"
