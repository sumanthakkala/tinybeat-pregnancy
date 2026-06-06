"""WeightLog ORM model — one weight measurement.

When this file changes (add a column, drop one, etc.), generate a new
Alembic migration from the plugin dir:

    ~/.hermes/hermes-agent/venv/bin/alembic revision --autogenerate -m "describe the change"

Commit both the model change AND the generated migration file under
``alembic/versions/``.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class WeightLog(Base):
    """One weight measurement, idempotent by ``idempotency_key``."""

    __tablename__ = "weight_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Stored as TEXT in SQLite so YYYY-MM-DD or full ISO 8601 both work
    # and sort correctly. The tool's prose validates the format.
    recorded_at: Mapped[str] = mapped_column(String, nullable=False, index=True)

    kg: Mapped[float] = mapped_column(Float, nullable=False)

    note: Mapped[str | None] = mapped_column(String, nullable=True)

    # Provenance (PRD-05 canonical metric shape; added in PRD-09 so PRD-13 can
    # route extracted weights here). source: self | report | device.
    # source_report_id is a plain nullable column for now — PRD-13 adds the
    # reports table + FK constraint when it lands.
    source: Mapped[str] = mapped_column(
        String, nullable=False, default="self", server_default="self",
    )
    source_report_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # The dedupe key. The handler does an INSERT-after-SELECT pattern;
    # the UNIQUE constraint catches the concurrent-insert race.
    idempotency_key: Mapped[str] = mapped_column(
        String, nullable=False, unique=True,
    )

    # When the *row* was created (vs when the measurement was taken).
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover — debug aid
        return f"<WeightLog id={self.id} recorded_at={self.recorded_at!r} kg={self.kg}>"
