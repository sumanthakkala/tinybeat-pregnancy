"""BpReading ORM model — one blood-pressure measurement (PRD-10).

Canonical metric shape (PRD-05) + BP specifics (systolic/diastolic/pulse/arm/
position). Red-flag handling (≥140/90 informational, ≥160/110 → PRD-17
escalation) lives in the FE guidance engine + the agent SKILL, not the schema.

After editing this model, autogenerate a migration from the plugin dir:
    ~/.hermes/hermes-agent/venv/bin/alembic revision --autogenerate -m "..."
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class BpReading(Base):
    """One blood-pressure reading, idempotent by ``idempotency_key``."""

    __tablename__ = "bp_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    recorded_at: Mapped[str] = mapped_column(String, nullable=False, index=True)

    systolic: Mapped[int] = mapped_column(Integer, nullable=False)
    diastolic: Mapped[int] = mapped_column(Integer, nullable=False)
    pulse: Mapped[int | None] = mapped_column(Integer, nullable=True)

    arm: Mapped[str | None] = mapped_column(String, nullable=True)  # left | right
    position: Mapped[str | None] = mapped_column(String, nullable=True)  # sitting | lying | standing

    note: Mapped[str | None] = mapped_column(String, nullable=True)

    # Provenance (canonical metric shape; PRD-13 routes extracted values here).
    source: Mapped[str] = mapped_column(
        String, nullable=False, default="self", server_default="self",
    )
    source_report_id: Mapped[str | None] = mapped_column(String, nullable=True)

    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<BpReading id={self.id} {self.systolic}/{self.diastolic} at {self.recorded_at!r}>"
