"""recent_symptoms — read recent symptom rows to ground an answer (PRD-16)."""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge.workflows import Tool
from .._reads import recent_symptoms

SCHEMA: dict = {
    "name": "recent_symptoms",
    "description": "Read the user's recently logged symptoms (read-only), to ground an answer in their history.",
    "parameters": {
        "type": "object",
        "properties": {"n": {"type": "integer", "description": "How many recent rows (default 20)."}},
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    return json.dumps(recent_symptoms(args.get("n", 20)))


TOOL = Tool(
    name="recent_symptoms",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Read recently logged symptoms (read-only).",
    emoji="📝",
)
