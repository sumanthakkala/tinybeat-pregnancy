"""byo.reports.list — reports + their proposed/confirmed counts (PRD-13).

Powers the Records "needs review" surface: any report with proposed_count > 0 is
awaiting the user's confirmation.
"""

from __future__ import annotations

from sqlalchemy import desc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.document import Document
from tinybeat_pregnancy.storage.models.extracted_value import ExtractedValue
from byoh_bridge.workflows import Rpc

_REPORT_KINDS = {"report", "scan", "prescription"}


def handler(_params: dict) -> dict:
    with storage.session() as s:
        counts: dict[str, dict] = {}
        for doc_id, status in s.execute(
            select(ExtractedValue.document_id, ExtractedValue.status)
        ).all():
            c = counts.setdefault(doc_id, {"proposed": 0, "confirmed": 0, "dismissed": 0})
            c[status] = c.get(status, 0) + 1

        docs = s.execute(select(Document).order_by(desc(Document.created_at))).scalars().all()
        rows = []
        for d in docs:
            c = counts.get(d.id)
            if d.kind not in _REPORT_KINDS and not c:
                continue
            rows.append({
                "document_id": d.id,
                "filename": d.filename,
                "kind": d.kind,
                "status": d.status,
                "title": d.title,
                "summary": d.summary,
                "proposed_count": (c or {}).get("proposed", 0),
                "confirmed_count": (c or {}).get("confirmed", 0),
                "created_at": d.created_at.isoformat() if d.created_at else None,
            })
    return {"rows": rows, "count": len(rows)}


RPC = Rpc(
    method="byo.reports.list",
    handler=handler,
    description="Reports with their proposed/confirmed value counts.",
    read_only=True,
)
