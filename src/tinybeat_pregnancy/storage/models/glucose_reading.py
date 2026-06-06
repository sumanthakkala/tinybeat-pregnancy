"""GlucoseReading ORM model — one blood-glucose measurement (PRD-11).

Canonical metric shape (PRD-05) + glucose context: the ``reading_type`` (fasting
vs post-meal) and ``unit`` are what make a value meaningful, since the target
band differs by type. Many values arrive via report extraction (PRD-13), so the
provenance columns matter here.

After editing, autogenerate a migration from the plugin dir:
    ~/.hermes/hermes-agent/venv/bin/alembic revision --autogenerate -m "..."
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class GlucoseReading(Base):
    """One blood-glucose reading, idempotent by ``idempotency_key``."""

    __tablename__ = "glucose_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    recorded_at: Mapped[str] = mapped_column(String, nullable=False, index=True)

    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)  # mg/dL | mmol/L (as logged)
    # fasting | post_meal_1h | post_meal_2h | random — selects the target band.
    reading_type: Mapped[str] = mapped_column(String, nullable=False)
    meal: Mapped[str | None] = mapped_column(String, nullable=True)  # what they ate (post-meal context)

    note: Mapped[str | None] = mapped_column(String, nullable=True)

    source: Mapped[str] = mapped_column(
        String, nullable=False, default="self", server_default="self",
    )
    source_report_id: Mapped[str | None] = mapped_column(String, nullable=True)

    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<GlucoseReading id={self.id} {self.value}{self.unit} {self.reading_type}>"
