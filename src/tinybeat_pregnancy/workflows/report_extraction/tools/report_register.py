"""report_register — mark a document as a report being processed (PRD-13)."""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.document import Document
from byoh_bridge.workflows import Tool

SCHEMA: dict = {
    "name": "report_register",
    "description": (
        "Mark the uploaded document as a medical report you're about to read. "
        "Call this once at the start. Sets the document to 'processing'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string", "description": "The document_id from the process request."},
            "kind": {"type": "string", "description": "report | scan | prescription | other (default report)."},
            "idempotency_key": {"type": "string", "description": "Stable key, e.g. 'register:<document_id>'."},
        },
        "required": ["document_id", "idempotency_key"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    doc_id = str(args.get("document_id", "")).strip()
    if not doc_id:
        return json.dumps({"ok": False, "error": "document_id required"})
    with storage.session() as s:
        d = s.get(Document, doc_id)
        if d is None:
            return json.dumps({"ok": False, "error": "unknown document"})
        d.status = "processing"
        d.kind = str(args.get("kind") or "report")
    return json.dumps({"ok": True, "document_id": doc_id})


TOOL = Tool(
    name="report_register",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Mark a document as a report being processed.",
    emoji="📄",
)
