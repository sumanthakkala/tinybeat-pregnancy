"""Document ORM model — an uploaded file living in the local inbox (PRD-07).

Shared infrastructure: report extraction (PRD-13), the records library (PRD-42),
and bump photos (PRD-32) all reference rows here. The bytes live on disk in
``inbox/``; this row is metadata only.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from byoh_bridge.storage import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # = inbox_id ("doc_…")
    filename: Mapped[str] = mapped_column(String, nullable=False)  # original name (display only)
    mime: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str | None] = mapped_column(String, nullable=True)
    inbox_path: Mapped[str] = mapped_column(String, nullable=False)  # absolute local path

    # report | scan | photo | prescription | other — refined by extraction/classify.
    kind: Mapped[str] = mapped_column(String, nullable=False, default="other", server_default="other")
    # received | processing | processed | failed
    status: Mapped[str] = mapped_column(String, nullable=False, default="received", server_default="received")

    title: Mapped[str | None] = mapped_column(String, nullable=True)  # agent-written (PRD-42)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)  # agent-written (PRD-42)
    taken_at: Mapped[str | None] = mapped_column(String, nullable=True)  # for photos/scans (week overlay)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.datetime("now"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Document id={self.id!r} kind={self.kind!r} status={self.status!r}>"
