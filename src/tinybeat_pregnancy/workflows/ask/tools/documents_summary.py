"""documents_summary — recent uploaded documents to ground an answer (PRD-16)."""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge.workflows import Tool
from .._reads import documents_summary

SCHEMA: dict = {
    "name": "documents_summary",
    "description": "Read the user's recent uploaded documents/reports with their titles + summaries (read-only).",
    "parameters": {
        "type": "object",
        "properties": {"n": {"type": "integer", "description": "How many recent docs (default 10)."}},
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    return json.dumps(documents_summary(args.get("n", 10)))


TOOL = Tool(
    name="documents_summary",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Read recent uploaded documents (read-only).",
    emoji="📄",
)
