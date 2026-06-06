"""ExtractedValue → plain dict (shared by the report RPCs)."""

from __future__ import annotations

import json
from typing import Any


def value_to_dict(v: Any) -> dict:
    try:
        parsed = json.loads(v.value_json)
    except Exception:
        parsed = {}
    return {
        "id": v.id,
        "document_id": v.document_id,
        "metric": v.metric,
        "value": parsed,
        "date": v.date,
        "page": v.page,
        "snippet": v.snippet,
        "confidence": v.confidence,
        "status": v.status,
        "target_row_table": v.target_row_table,
        "target_row_id": v.target_row_id,
        "confirmed_at": v.confirmed_at.isoformat() if v.confirmed_at else None,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }
