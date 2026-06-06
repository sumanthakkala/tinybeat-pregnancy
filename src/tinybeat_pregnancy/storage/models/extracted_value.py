"""ExtractedValue ORM model — the report-extraction staging + audit table (PRD-13).

The trust linchpin (§6.3): values the agent reads out of an uploaded report land
here as ``status="proposed"`` — **never** straight into the metric tables. They
become official only when the user taps confirm (``byo.report.confirm``), which
writes the real metric row and stamps ``confirmed_at`` here. This row keeps the
full provenance (document + page + snippet + model + timestamps) — the seed of
the PRD-43 audit trail.

After editing, autogenerate a migration from the plugin dir:
    ~/.hermes/hermes-agent/venv/bin/alembic revision --autogenerate -m "..."
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class ExtractedValue(Base):
    __tablename__ = "extracted_values"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # "xv_…"
    document_id: Mapped[str] = mapped_column(
        String, ForeignKey("documents.id"), nullable=False, index=True,
    )

    # Which dashboard it targets: weight | bp | glucose | hemoglobin | hcg | tsh |
    # blood_type | fundal_height | edd | other.
    metric: Mapped[str] = mapped_column(String, nullable=False)
    # JSON payload; shape depends on metric (e.g. {"kg":67.4}, {"sys":118,"dia":76}).
    value_json: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str | None] = mapped_column(String, nullable=True)  # measurement date (ISO)

    # Provenance.
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    snippet: Mapped[str | None] = mapped_column(String, nullable=True)  # verbatim source text
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)  # which model extracted

    # Lifecycle: proposed | confirmed | dismissed.
    status: Mapped[str] = mapped_column(String, nullable=False, default="proposed", server_default="proposed")
    # Set on confirm — where the value landed (audit).
    target_row_table: Mapped[str | None] = mapped_column(String, nullable=True)
    target_row_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Idempotency for re-processing the same report (one proposal per logical value).
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ExtractedValue {self.id} {self.metric} {self.status}>"
