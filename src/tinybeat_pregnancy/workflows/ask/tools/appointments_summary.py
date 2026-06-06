"""appointments_summary — upcoming + recent visits to ground an answer (PRD-16)."""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge.workflows import Tool
from .._reads import appointments_summary

SCHEMA: dict = {
    "name": "appointments_summary",
    "description": "Read the user's upcoming and recent appointments (read-only).",
    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
}


def handler(_args: dict[str, Any], **_: Any) -> str:
    return json.dumps(appointments_summary())


TOOL = Tool(
    name="appointments_summary",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Read upcoming + recent appointments (read-only).",
    emoji="📅",
)
