"""byo.documents.list — recent uploaded documents for the UI."""

from __future__ import annotations

from sqlalchemy import desc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.document import Document
from byoh_bridge.workflows import Rpc


def _serialize(d: Document) -> dict:
    return {
        "id": d.id,
        "filename": d.filename,
        "mime": d.mime,
        "size_bytes": d.size_bytes,
        "kind": d.kind,
        "status": d.status,
        "title": d.title,
        "summary": d.summary,
        "taken_at": d.taken_at,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


def handler(params: dict) -> dict:
    limit = int(params.get("limit", 50) or 50)
    with storage.session() as s:
        rows = s.execute(select(Document).order_by(desc(Document.created_at)).limit(limit)).scalars().all()
        payload = [_serialize(r) for r in rows]
    return {"rows": payload, "count": len(payload)}


RPC = Rpc(method="byo.documents.list", handler=handler, description="Recent uploaded documents.", read_only=True)
