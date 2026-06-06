"""Read-only data helpers for the Ask assistant (PRD-16).

The Ask agent grounds its answers in the user's own rows. These query the same
tables the UI read-RPCs do, but as agent-callable tool payloads — and they are
**read-only** (Ask never writes; §7). Shared here so the four Ask tools (and
later the digest, PRD-29) stay consistent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import desc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from tinybeat_pregnancy.storage.models.bp_reading import BpReading
from tinybeat_pregnancy.storage.models.document import Document
from tinybeat_pregnancy.storage.models.glucose_reading import GlucoseReading
from tinybeat_pregnancy.storage.models.symptom_log import SymptomLog
from tinybeat_pregnancy.storage.models.weight_log import WeightLog

_METRIC_MODELS = {"weight": WeightLog, "bp": BpReading, "glucose": GlucoseReading}


def _metric_row(metric: str, r: Any) -> dict:
    base = {"recorded_at": r.recorded_at, "source": getattr(r, "source", "self")}
    if metric == "weight":
        base["kg"] = r.kg
    elif metric == "bp":
        base.update(systolic=r.systolic, diastolic=r.diastolic, pulse=r.pulse)
    elif metric == "glucose":
        base.update(value=r.value, unit=r.unit, reading_type=r.reading_type)
    if getattr(r, "note", None):
        base["note"] = r.note
    return base


def recent_metric(metric: str, n: int = 10) -> dict:
    model = _METRIC_MODELS.get(metric)
    if model is None:
        return {"ok": False, "error": f"unknown metric: {metric} (use weight | bp | glucose)"}
    n = max(1, min(int(n or 10), 100))
    with storage.session() as s:
        rows = (
            s.execute(select(model).order_by(desc(model.recorded_at), desc(model.id)).limit(n))
            .scalars()
            .all()
        )
        out = [_metric_row(metric, r) for r in rows]
    return {"ok": True, "metric": metric, "count": len(out), "rows": out}


def recent_symptoms(n: int = 20) -> dict:
    n = max(1, min(int(n or 20), 200))
    with storage.session() as s:
        rows = (
            s.execute(select(SymptomLog).order_by(desc(SymptomLog.recorded_at), desc(SymptomLog.id)).limit(n))
            .scalars()
            .all()
        )
        out = [{"recorded_at": r.recorded_at, "symptom": r.symptom, "severity": r.severity} for r in rows]
    return {"ok": True, "count": len(out), "rows": out}


def appointments_summary() -> dict:
    now16 = datetime.now().isoformat()[:16]
    with storage.session() as s:
        rows = s.execute(select(Appointment)).scalars().all()

    def fmt(a: Any) -> dict:
        return {"starts_at": a.starts_at, "kind": a.kind, "provider": a.provider, "location": a.location, "status": a.status}

    upcoming = sorted(
        (a for a in rows if a.status == "scheduled" and a.starts_at[:16] >= now16), key=lambda a: a.starts_at
    )[:5]
    recent = sorted(
        (a for a in rows if not (a.status == "scheduled" and a.starts_at[:16] >= now16)),
        key=lambda a: a.starts_at,
        reverse=True,
    )[:5]
    return {"ok": True, "upcoming": [fmt(a) for a in upcoming], "recent": [fmt(a) for a in recent]}


def documents_summary(n: int = 10) -> dict:
    n = max(1, min(int(n or 10), 50))
    with storage.session() as s:
        rows = s.execute(select(Document).order_by(desc(Document.created_at)).limit(n)).scalars().all()
        out = [
            {"filename": d.filename, "kind": d.kind, "status": d.status, "title": d.title, "summary": d.summary}
            for d in rows
        ]
    return {"ok": True, "count": len(out), "rows": out}
