"""Profile ORM model — the single-row (id=1) facts the product is computed from.

After changing this file, regenerate the migration:
    ~/.hermes/hermes-agent/venv/bin/alembic revision --autogenerate -m "describe change"
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class Profile(Base):
    """One row, ``id=1``. Due date drives the gestational-week engine (PRD-03)."""

    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True)  # always 1

    name: Mapped[str | None] = mapped_column(String, nullable=True)

    # Estimated due date (EDD). If absent, derive from lmp_date (LMP + 280d).
    due_date: Mapped[str | None] = mapped_column(String, nullable=True)
    lmp_date: Mapped[str | None] = mapped_column(String, nullable=True)
    edd_source: Mapped[str | None] = mapped_column(String, nullable=True)  # due_date|lmp|ultrasound

    prepreg_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)

    units_weight: Mapped[str] = mapped_column(String, nullable=False, default="kg", server_default="kg")
    units_length: Mapped[str] = mapped_column(String, nullable=False, default="cm", server_default="cm")

    emergency_contact_name: Mapped[str | None] = mapped_column(String, nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String, nullable=True)

    postpartum: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    birth_date: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"), onupdate=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Profile due_date={self.due_date!r} name={self.name!r}>"
