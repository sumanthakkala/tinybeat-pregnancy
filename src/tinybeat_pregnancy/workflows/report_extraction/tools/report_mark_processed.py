"""report_mark_processed — finalize a report with a title + summary (PRD-13)."""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.document import Document
from byoh_bridge.workflows import Tool

SCHEMA: dict = {
    "name": "report_mark_processed",
    "description": (
        "Finish processing the report: save a short plain-language title and summary, "
        "and mark the document 'processed'. Call this last, after proposing all values."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string"},
            "title": {"type": "string", "description": "A short human title, e.g. 'Routine labs — May 12'."},
            "summary": {"type": "string", "description": "A plain-language summary of what's in the report."},
            "idempotency_key": {"type": "string", "description": "Stable key, e.g. 'processed:<document_id>'."},
        },
        "required": ["document_id", "title", "summary", "idempotency_key"],
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
        d.title = str(args.get("title") or d.title)
        d.summary = str(args.get("summary") or d.summary)
        d.status = "processed"
    return json.dumps({"ok": True, "document_id": doc_id})


TOOL = Tool(
    name="report_mark_processed",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Finalize a report with a title + summary and mark it processed.",
    emoji="✅",
)
