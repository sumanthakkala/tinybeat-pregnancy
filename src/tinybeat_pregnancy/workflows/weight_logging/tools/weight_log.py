"""weight_log — record one weight measurement to the local tracker.

One tool, one file. Schema, handler, and ``TOOL`` definition co-located.
The handler now uses SQLAlchemy sessions + the ``WeightLog`` model class
instead of raw SQL.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.weight_log import WeightLog
from byoh_bridge.workflows import Tool

logger = logging.getLogger(__name__)


# ── Schema (model contract) ──────────────────────────────────────────────

SCHEMA: dict = {
    "name": "weight_log",
    "description": (
        "Record one weight measurement to the user's local pregnancy tracker. "
        "Use only when the user provides a weight value. "
        "ALWAYS supply a stable idempotency_key derived from the source "
        "(e.g. 'manual:2026-05-24' or 'report:rpt_001:weight:1'). "
        "Re-runs with the same key are no-ops."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "recorded_at": {
                "type": "string",
                "description": (
                    "Date or ISO timestamp of the measurement "
                    "(YYYY-MM-DD or full ISO 8601)."
                ),
            },
            "kg": {
                "type": "number",
                "description": "Weight in kilograms. Must be > 0 and < 500.",
            },
            "note": {
                "type": "string",
                "description": "Optional free-text note (e.g. 'fasted morning weight').",
            },
            "source": {
                "type": "string",
                "description": (
                    "Where the value came from: self | report | device. "
                    "Default 'self' (the user told you). Use 'report' only when "
                    "logging a value extracted from an uploaded document."
                ),
            },
            "source_report_id": {
                "type": "string",
                "description": "When source='report', the document/report id it came from.",
            },
            "idempotency_key": {
                "type": "string",
                "description": "Stable key for de-duplication. Required.",
            },
        },
        "required": ["recorded_at", "kg", "idempotency_key"],
        "additionalProperties": False,
    },
}


# ── Handler ──────────────────────────────────────────────────────────────


def handler(args: dict[str, Any], **_: Any) -> str:
    """Insert one weight reading. Idempotent by ``idempotency_key``."""
    recorded_at = str(args.get("recorded_at", "")).strip()
    raw_kg = args.get("kg")
    note = args.get("note")
    source = (str(args.get("source") or "self").strip() or "self")
    source_report_id = args.get("source_report_id") or None
    key = str(args.get("idempotency_key", "")).strip()

    # Defensive validation (model API already checks the schema; this
    # catches bugs from a misbehaving provider or future schema drift).
    if not recorded_at or not key:
        return _err("recorded_at and idempotency_key required")
    try:
        kg = float(raw_kg)
    except (TypeError, ValueError):
        return _err("kg must be a number")
    if not (0 < kg < 500):
        return _err("kg out of plausible range")

    with storage.session() as s:
        # Idempotency: look up by key first; same key → return existing row.
        existing = s.scalar(
            select(WeightLog).where(WeightLog.idempotency_key == key)
        )
        if existing is not None:
            return _ok(
                id=existing.id,
                deduped=True,
                message=f"already recorded as id={existing.id}",
            )

        row = WeightLog(
            recorded_at=recorded_at,
            kg=kg,
            note=note,
            source=source,
            source_report_id=source_report_id,
            idempotency_key=key,
        )
        s.add(row)
        s.flush()  # populates row.id without ending the transaction
        row_id = row.id

    logger.info(
        "[weight_log] logged kg=%s recorded_at=%s id=%s",
        kg, recorded_at, row_id,
    )
    return _ok(id=row_id, recorded_at=recorded_at, kg=kg)


# ── Helpers (file-local) ─────────────────────────────────────────────────


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields})


def _err(message: str) -> str:
    return json.dumps({"ok": False, "error": message})


# ── Tool registration ────────────────────────────────────────────────────

TOOL = Tool(
    name="weight_log",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Record one weight measurement to the local pregnancy tracker.",
    emoji="⚖️",
)
