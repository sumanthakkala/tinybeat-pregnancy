"""symptom_log — record one symptom occurrence (PRD-12).

Hand-written (not the metric factory) because it has two specifics:
- the ``symptom`` is validated against the taxonomy (so a typo'd key can't slip
  into the heatmap), and
- re-logging the same symptom/day **updates severity** rather than no-op'ing (the
  factory's pure-idempotent insert can't), so a correction lands.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.symptom_log import SymptomLog
from byoh_bridge.workflows import Tool
from .._taxonomy import KEYS, is_red_flag

logger = logging.getLogger(__name__)

SCHEMA: dict = {
    "name": "symptom_log",
    "description": (
        "Record one symptom the user is experiencing, into their local tracker. "
        "Call once per distinct symptom. 'symptom' MUST be a taxonomy key (map the "
        "user's words to the closest key). severity is 1 (mild) | 2 (moderate) | 3 "
        "(severe), optional. ALWAYS supply idempotency_key 'manual:<date>:<symptom>' "
        "— re-logging the same symptom/day updates its severity. For any red-flag "
        "symptom, follow the safety guidance: surface the escalation in your reply."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "recorded_at": {"type": "string", "description": "Date YYYY-MM-DD (today unless stated)."},
            "symptom": {"type": "string", "description": "Taxonomy key.", "enum": sorted(KEYS)},
            "severity": {"type": "integer", "description": "1 mild | 2 moderate | 3 severe (optional)."},
            "note": {"type": "string", "description": "Optional free-text detail."},
            "source": {"type": "string", "description": "self | report | device (default self)."},
            "idempotency_key": {"type": "string", "description": "Stable key 'manual:<date>:<symptom>'."},
        },
        "required": ["recorded_at", "symptom", "idempotency_key"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    recorded_at = str(args.get("recorded_at", "")).strip()
    symptom = str(args.get("symptom", "")).strip()
    key = str(args.get("idempotency_key", "")).strip()
    note = args.get("note")
    source = (str(args.get("source") or "self").strip() or "self")
    raw_sev = args.get("severity")

    if not recorded_at or not symptom or not key:
        return _err("recorded_at, symptom and idempotency_key required")
    if symptom not in KEYS:
        return _err(f"unknown symptom key: {symptom}")
    severity: int | None = None
    if raw_sev is not None:
        try:
            severity = int(raw_sev)
        except (TypeError, ValueError):
            return _err("severity must be an integer 1-3")
        if severity not in (1, 2, 3):
            return _err("severity must be 1, 2 or 3")

    with storage.session() as s:
        existing = s.scalar(select(SymptomLog).where(SymptomLog.idempotency_key == key))
        if existing is not None:
            # Re-log → update severity/note (a correction), keep the row.
            if severity is not None:
                existing.severity = severity
            if note is not None:
                existing.note = note
            s.flush()
            return _ok(id=existing.id, symptom=symptom, updated=True, red_flag=is_red_flag(symptom))

        row = SymptomLog(
            recorded_at=recorded_at,
            symptom=symptom,
            severity=severity,
            note=note,
            source=source,
            idempotency_key=key,
        )
        s.add(row)
        s.flush()
        row_id = row.id

    logger.info("[symptom_log] %s sev=%s at %s id=%s", symptom, severity, recorded_at, row_id)
    return _ok(id=row_id, symptom=symptom, red_flag=is_red_flag(symptom))


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields})


def _err(message: str) -> str:
    return json.dumps({"ok": False, "error": message})


TOOL = Tool(
    name="symptom_log",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Record one symptom (taxonomy key + optional severity) to the local tracker.",
    emoji="📝",
)
