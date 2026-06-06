"""byo.reports.proposals{document_id} — staged values for the confirmation screen."""

from __future__ import annotations

from sqlalchemy import asc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.document import Document
from tinybeat_pregnancy.storage.models.extracted_value import ExtractedValue
from byoh_bridge.workflows import Rpc
from ._serialize import value_to_dict


def handler(params: dict) -> dict:
    doc_id = str(params.get("document_id") or "")
    with storage.session() as s:
        doc = s.get(Document, doc_id) if doc_id else None
        rows = (
            s.execute(
                select(ExtractedValue)
                .where(ExtractedValue.document_id == doc_id)
                .order_by(asc(ExtractedValue.created_at), asc(ExtractedValue.id))
            )
            .scalars()
            .all()
        )
        values = [value_to_dict(v) for v in rows]
        document = (
            {
                "id": doc.id,
                "filename": doc.filename,
                "mime": doc.mime,
                "kind": doc.kind,
                "status": doc.status,
                "title": doc.title,
                "summary": doc.summary,
            }
            if doc
            else None
        )
    proposed = [v for v in values if v["status"] == "proposed"]
    return {"document": document, "values": values, "proposed_count": len(proposed)}


RPC = Rpc(
    method="byo.reports.proposals",
    handler=handler,
    description="Staged extracted values for a document (for the confirmation screen).",
    read_only=True,
)
