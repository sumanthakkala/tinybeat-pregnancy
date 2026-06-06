"""recent_metrics — read recent weight/BP/glucose rows to ground an answer (PRD-16)."""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge.workflows import Tool
from .._reads import recent_metric

SCHEMA: dict = {
    "name": "recent_metrics",
    "description": (
        "Read the user's most recent measurements for one metric, to ground your "
        "answer in their real data. Read-only. Reference what you read in your reply "
        "(e.g. 'your last 3 BP readings were …')."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "metric": {"type": "string", "enum": ["weight", "bp", "glucose"]},
            "n": {"type": "integer", "description": "How many recent rows (default 10)."},
        },
        "required": ["metric"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    return json.dumps(recent_metric(str(args.get("metric", "")), args.get("n", 10)))


TOOL = Tool(
    name="recent_metrics",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Read recent weight/BP/glucose rows (read-only).",
    emoji="📈",
)
