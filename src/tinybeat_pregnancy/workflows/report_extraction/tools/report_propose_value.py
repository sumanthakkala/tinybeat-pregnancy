"""report_propose_value — stage one value read from a report (PRD-13).

Writes to ``extracted_values`` (status="proposed"), NEVER to a metric table —
that only happens after the user confirms (§6.3). Narrow per-metric validation
in the handler is the guard against a decimal-point misread sneaking through.
"""

from __future__ import annotations

import json
import secrets
from typing import Any

from sqlalchemy import select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.document import Document
from tinybeat_pregnancy.storage.models.extracted_value import ExtractedValue
from byoh_bridge.workflows import Tool
from .._metrics import METRICS, validate

SCHEMA: dict = {
    "name": "report_propose_value",
    "description": (
        "Propose ONE value you actually read in the document. It is staged for the "
        "user to confirm — it does NOT go into any chart yet. Never invent a value "
        "that isn't in the document; prefer a low confidence over false precision. "
        "Provide a verbatim snippet + page so the user can check the source. "
        "value is a JSON object whose shape depends on metric: "
        "weight {kg} · bp {sys,dia,pulse?} · glucose {value,unit,reading_type} · "
        "fundal_height {cm} · hemoglobin/hcg/tsh {value,unit} · blood_type {type} · "
        "edd {date} · other {label,value,unit?}."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string"},
            "metric": {"type": "string", "enum": sorted(METRICS)},
            "value": {"type": "object", "description": "Metric-specific value object (see description)."},
            "date": {"type": "string", "description": "Measurement date YYYY-MM-DD if present in the doc."},
            "page": {"type": "integer", "description": "Page number the value appears on."},
            "snippet": {"type": "string", "description": "Short verbatim source text containing the value."},
            "confidence": {"type": "number", "description": "0.0–1.0 calibrated confidence."},
            "idempotency_key": {"type": "string", "description": "Stable key, e.g. '<document_id>:weight:1'."},
        },
        "required": ["document_id", "metric", "value", "idempotency_key"],
        "additionalProperties": False,
    },
}


def handler(args: dict[str, Any], **_: Any) -> str:
    doc_id = str(args.get("document_id", "")).strip()
    metric = str(args.get("metric", "")).strip()
    value = args.get("value")
    key = str(args.get("idempotency_key", "")).strip()
    if not doc_id or not metric or not key:
        return _err("document_id, metric and idempotency_key required")
    if metric not in METRICS:
        return _err(f"unknown metric: {metric}")
    if not isinstance(value, dict):
        return _err("value must be a JSON object")
    verr = validate(metric, value)
    if verr:
        return _err(verr)

    conf = args.get("confidence")
    page = args.get("page")
    with storage.session() as s:
        if s.get(Document, doc_id) is None:
            return _err("unknown document")
        existing = s.scalar(select(ExtractedValue).where(ExtractedValue.idempotency_key == key))
        if existing is not None:
            return _ok(id=existing.id, deduped=True)
        ev = ExtractedValue(
            id="xv_" + secrets.token_hex(8),
            document_id=doc_id,
            metric=metric,
            value_json=json.dumps(value),
            date=(str(args.get("date")) if args.get("date") else None),
            page=(int(page) if isinstance(page, (int, float)) else None),
            snippet=(str(args.get("snippet")) if args.get("snippet") else None),
            confidence=(float(conf) if isinstance(conf, (int, float)) else None),
            model=(str(args.get("model")) if args.get("model") else None),
            status="proposed",
            idempotency_key=key,
        )
        s.add(ev)
        s.flush()
        ev_id = ev.id
    return _ok(id=ev_id, metric=metric)


def _ok(**f: Any) -> str:
    return json.dumps({"ok": True, **f})


def _err(message: str) -> str:
    return json.dumps({"ok": False, "error": message})


TOOL = Tool(
    name="report_propose_value",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Stage one value extracted from a report for the user to confirm.",
    emoji="🔎",
)
