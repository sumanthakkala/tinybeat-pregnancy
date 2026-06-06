"""byo.journey.overlay — week-keyed aggregation of the user's real data (PRD-08).

The Journey scroll is mostly *generic* per-week content bundled in the UI; this
one read layers the user's **own** history on top of it. It walks the feature
tables that exist, maps each row's date → gestational week (using the same
``_week`` engine the rest of the product runs on), and buckets the rows into
"memory cards" the FE docks to the matching week.

Design notes:
- **One read, not N.** The FE calls this once and renders every week from the
  result (cached via PRD-04 so it paints while the agent is asleep).
- **Degrade gracefully.** Each source is wrapped in try/except so a missing or
  empty table (or a future schema change) never breaks the whole overlay — that
  week's cards simply don't appear. New data PRDs (11 glucose, 13 reports, 21
  kicks, 31 journal, 32 photos…) register their source by adding a ``_source``.
- **No tables of its own.** Pure denormalized view; nothing to migrate.

Result shape::

    {"weeks": {"<week>": {"items": [
        {kind, title, subtitle?, value?, values?, deeplink, source_id}, ...
    ]}}}
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import asc, select

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.appointment import Appointment
from tinybeat_pregnancy.storage.models.bp_reading import BpReading
from tinybeat_pregnancy.storage.models.document import Document
from tinybeat_pregnancy.storage.models.glucose_reading import GlucoseReading
from tinybeat_pregnancy.storage.models.profile import Profile
from tinybeat_pregnancy.storage.models.symptom_log import SymptomLog
from tinybeat_pregnancy.storage.models.weight_log import WeightLog
from byoh_bridge.workflows import Rpc
from ...profile._week import edd_from_lmp, gestation
from ...symptoms._taxonomy import is_red_flag, label_of

logger = logging.getLogger(__name__)

# The Journey renders weeks 4..40; clamp every bucket into that range so a row
# dated just before/after the term still lands on a visible week.
MIN_WEEK = 4
MAX_WEEK = 40

_DOC_LABELS = {
    "report": "Report",
    "scan": "Scan",
    "photo": "Photo",
    "prescription": "Prescription",
}


def _edd_for(p: Profile | None) -> str | None:
    """The estimated due date used to date every row (due_date, else LMP+280)."""
    if p is None:
        return None
    if p.due_date:
        return p.due_date
    if p.lmp_date:
        return edd_from_lmp(p.lmp_date)
    return None


def _week_for(edd: str, iso: str | None) -> int | None:
    """Gestational week for an ISO date/datetime, clamped to the visible range."""
    if not iso:
        return None
    day = str(iso)[:10]  # tolerate full ISO timestamps; the week engine wants a date
    try:
        wk = int(gestation(edd, day)["week"])
    except Exception:
        return None
    return max(MIN_WEEK, min(MAX_WEEK, wk))


def _bucket(weeks: dict[int, list[dict]], wk: int, item: dict) -> None:
    weeks.setdefault(wk, []).append(item)


# ── Sources (each wrapped by the handler; add one per data PRD) ──────────────


def _source_weight(s, edd: str, weeks: dict[int, list[dict]]) -> None:
    """Weight readings → one card per lived week, with a to-date sparkline."""
    rows = (
        s.execute(select(WeightLog).order_by(asc(WeightLog.recorded_at), asc(WeightLog.id)))
        .scalars()
        .all()
    )
    # Chronological (week, kg) pairs; rows are already date-ordered.
    series: list[tuple[int, float]] = []
    for r in rows:
        wk = _week_for(edd, r.recorded_at)
        if wk is not None:
            series.append((wk, float(r.kg)))
    if not series:
        return
    for wk in sorted({w for w, _ in series}):
        upto = [kg for (w, kg) in series if w <= wk]
        latest_this_week = [kg for (w, kg) in series if w == wk][-1]
        _bucket(
            weeks,
            wk,
            {
                "kind": "weight",
                "title": "Weight",
                "value": f"{latest_this_week:g} kg",
                # ≥2 points makes a meaningful sparkline; else just the value.
                "values": [round(v, 2) for v in upto] if len(upto) >= 2 else None,
                "deeplink": "/track",
                "source_id": f"weight:{wk}",
            },
        )


def _source_documents(s, edd: str, weeks: dict[int, list[dict]]) -> None:
    """Uploaded reports/scans/photos → a card on the week they were taken."""
    rows = (
        s.execute(select(Document).order_by(asc(Document.created_at)).limit(500))
        .scalars()
        .all()
    )
    for d in rows:
        when = d.taken_at or (d.created_at.isoformat() if d.created_at else None)
        wk = _week_for(edd, when)
        if wk is None:
            continue
        kind = d.kind or "other"
        label = _DOC_LABELS.get(kind, "Document")
        _bucket(
            weeks,
            wk,
            {
                "kind": "photo" if kind == "photo" else "document",
                "title": d.title or label,
                "subtitle": d.filename,
                "deeplink": "/records",
                "source_id": d.id,
            },
        )


def _source_bp(s, edd: str, weeks: dict[int, list[dict]]) -> None:
    """BP readings → one card per lived week (the latest reading that week)."""
    rows = (
        s.execute(select(BpReading).order_by(asc(BpReading.recorded_at), asc(BpReading.id)))
        .scalars()
        .all()
    )
    latest_by_week: dict[int, BpReading] = {}
    for r in rows:
        wk = _week_for(edd, r.recorded_at)
        if wk is not None:
            latest_by_week[wk] = r  # rows are date-ordered, so last write wins
    for wk, r in latest_by_week.items():
        _bucket(
            weeks,
            wk,
            {
                "kind": "bp",
                "title": "Blood pressure",
                "value": f"{r.systolic}/{r.diastolic}",
                "deeplink": "/track",
                "source_id": f"bp:{wk}",
            },
        )


def _source_glucose(s, edd: str, weeks: dict[int, list[dict]]) -> None:
    """Glucose readings → one card per lived week (latest reading that week)."""
    rows = (
        s.execute(select(GlucoseReading).order_by(asc(GlucoseReading.recorded_at), asc(GlucoseReading.id)))
        .scalars()
        .all()
    )
    latest_by_week: dict[int, GlucoseReading] = {}
    for r in rows:
        wk = _week_for(edd, r.recorded_at)
        if wk is not None:
            latest_by_week[wk] = r
    _types = {"fasting": "fasting", "post_meal_1h": "1h post-meal", "post_meal_2h": "2h post-meal", "random": ""}
    for wk, r in latest_by_week.items():
        ctx = _types.get(r.reading_type, "")
        _bucket(
            weeks,
            wk,
            {
                "kind": "glucose",
                "title": "Glucose",
                "value": f"{r.value:g} {r.unit}",
                "subtitle": ctx or None,
                "deeplink": "/track",
                "source_id": f"glucose:{wk}",
            },
        )


def _source_symptoms(s, edd: str, weeks: dict[int, list[dict]]) -> None:
    """Symptoms → one card per lived week listing what was noted (🚩 if concerning)."""
    rows = (
        s.execute(select(SymptomLog).order_by(asc(SymptomLog.recorded_at), asc(SymptomLog.id)))
        .scalars()
        .all()
    )
    per_week: dict[int, dict] = {}
    for r in rows:
        wk = _week_for(edd, r.recorded_at)
        if wk is None:
            continue
        e = per_week.setdefault(wk, {"labels": [], "flagged": False})
        lbl = label_of(r.symptom)
        if lbl not in e["labels"]:
            e["labels"].append(lbl)
        if is_red_flag(r.symptom):
            e["flagged"] = True
    for wk, e in per_week.items():
        labels = e["labels"]
        subtitle = ", ".join(labels[:4]) + ("…" if len(labels) > 4 else "")
        _bucket(
            weeks,
            wk,
            {
                "kind": "symptom",
                "title": "Symptoms noted",
                "subtitle": subtitle,
                "value": "🚩" if e["flagged"] else None,
                "deeplink": "/track",
                "source_id": f"symptom:{wk}",
            },
        )


def _source_appointments(s, edd: str, weeks: dict[int, list[dict]]) -> None:
    """Appointments → a week-keyed marker (kind + provider) for the timeline."""
    rows = (
        s.execute(select(Appointment).where(Appointment.status != "cancelled"))
        .scalars()
        .all()
    )
    for a in rows:
        wk = _week_for(edd, a.starts_at)
        if wk is None:
            continue
        _bucket(
            weeks,
            wk,
            {
                "kind": "appointment",
                "title": a.kind,
                "subtitle": a.provider or None,
                "deeplink": "/care",
                "source_id": f"appt:{a.id}",
            },
        )


_SOURCES = (
    _source_weight, _source_bp, _source_glucose, _source_symptoms,
    _source_appointments, _source_documents,
)


# ── Handler ──────────────────────────────────────────────────────────────────


def handler(_params: dict) -> dict:
    weeks: dict[int, list[dict]] = {}
    with storage.session() as s:
        edd = _edd_for(s.get(Profile, 1))
        if edd:
            for src in _SOURCES:
                try:
                    src(s, edd, weeks)
                except Exception as exc:  # one bad/missing source must not sink the overlay
                    logger.warning("[journey.overlay] source %s skipped: %s", src.__name__, exc)
    # JSON object keys are strings; emit sorted for stable output.
    out: dict[str, Any] = {str(wk): {"items": items} for wk, items in sorted(weeks.items())}
    return {"weeks": out}


RPC = Rpc(
    method="byo.journey.overlay",
    handler=handler,
    description="Week-keyed overlay of the user's real milestones/metrics for the Journey.",
    read_only=True,
)
