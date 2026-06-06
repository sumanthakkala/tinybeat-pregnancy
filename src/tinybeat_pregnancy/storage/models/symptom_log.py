"""SymptomLog ORM model — one symptom occurrence (PRD-12).

One row per (symptom, day): keeps the heatmap/frequency queries simple and lets
red-flags be evaluated per row. Idempotent by ``idempotency_key`` =
``manual:<date>:<symptom>``; re-logging the same symptom/day updates severity.

After editing, autogenerate a migration from the plugin dir:
    ~/.hermes/hermes-agent/venv/bin/alembic revision --autogenerate -m "..."
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class SymptomLog(Base):
    """One logged symptom, idempotent by ``idempotency_key``."""

    __tablename__ = "symptom_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    recorded_at: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # A taxonomy key (workflows/symptoms/_taxonomy.py) — indexed for frequency.
    symptom: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # 1 mild · 2 moderate · 3 severe (optional).
    severity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    note: Mapped[str | None] = mapped_column(String, nullable=True)

    source: Mapped[str] = mapped_column(
        String, nullable=False, default="self", server_default="self",
    )

    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SymptomLog id={self.id} {self.symptom!r} sev={self.severity} at {self.recorded_at!r}>"
