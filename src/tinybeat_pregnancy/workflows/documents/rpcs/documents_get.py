"""byo.documents.get — one document's metadata."""

from __future__ import annotations

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.document import Document
from byoh_bridge.workflows import Rpc
from .documents_list import _serialize


def handler(params: dict) -> dict:
    doc_id = str(params.get("document_id") or params.get("id") or "")
    with storage.session() as s:
        doc = s.get(Document, doc_id)
        return {"document": _serialize(doc) if doc else None}


RPC = Rpc(method="byo.documents.get", handler=handler, description="One document's metadata.", read_only=True)
