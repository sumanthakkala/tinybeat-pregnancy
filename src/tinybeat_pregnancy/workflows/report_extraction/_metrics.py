"""Per-metric validation + confirm-write logic (PRD-13).

Shared by ``report_propose_value`` (narrow validation at propose time) and
``byo.report.confirm`` (write the confirmed value into its real metric table,
reusing the metric models with ``source="report"`` provenance). One place so the
two never drift.
"""

from __future__ import annotations

from typing import Any

from tinybeat_pregnancy.storage.models.bp_reading import BpReading
from tinybeat_pregnancy.storage.models.glucose_reading import GlucoseReading
from tinybeat_pregnancy.storage.models.weight_log import WeightLog

# Metrics the agent may propose.
METRICS = frozenset({
    "weight", "bp", "glucose", "hemoglobin", "hcg", "tsh",
    "blood_type", "fundal_height", "edd", "other",
})

# Metrics that confirm into a real metric table today (the built dashboards).
TABLE_METRICS = frozenset({"weight", "bp", "glucose"})


def _num(v: Any) -> float | None:
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def validate(metric: str, value: dict) -> str | None:
    """Narrow sanity check at propose time (catches the decimal-point misread).

    Returns an error string, or None if plausible. Non-table metrics get light
    validation (they're staged for the records library, not charted yet).
    """
    if metric not in METRICS:
        return f"unknown metric: {metric}"
    if not isinstance(value, dict):
        return "value must be an object"

    if metric == "weight":
        kg = _num(value.get("kg"))
        if kg is None or not (0 < kg < 500):
            return "weight.kg out of plausible range (0–500)"
    elif metric == "bp":
        sys, dia = _num(value.get("sys")), _num(value.get("dia"))
        if sys is None or not (50 <= sys <= 300):
            return "bp.sys out of plausible range (50–300)"
        if dia is None or not (30 <= dia <= 200):
            return "bp.dia out of plausible range (30–200)"
    elif metric == "glucose":
        val = _num(value.get("value"))
        if val is None or val <= 0:
            return "glucose.value must be positive"
        if value.get("unit") not in ("mg/dL", "mmol/L"):
            return "glucose.unit must be mg/dL or mmol/L"
        if value.get("reading_type") not in ("fasting", "post_meal_1h", "post_meal_2h", "random"):
            return "glucose.reading_type invalid"
    elif metric == "fundal_height":
        cm = _num(value.get("cm"))
        if cm is None or not (5 <= cm <= 60):
            return "fundal_height.cm out of plausible range"
    elif metric == "edd":
        if not value.get("date"):
            return "edd needs a date"
    # hemoglobin / hcg / tsh / blood_type / other: stored as-is for the library.
    return None


def write_metric_row(s, metric: str, value: dict, date: str, document_id: str, key: str):
    """Insert the confirmed value into its metric table. Returns (table, row_id) or None.

    None means "no chart for this metric yet" — the caller keeps it staged-confirmed
    (edd is handled separately by the confirm RPC → profile).
    """
    if metric == "weight":
        row = WeightLog(
            recorded_at=date, kg=float(value["kg"]),
            source="report", source_report_id=document_id, idempotency_key=key,
        )
    elif metric == "bp":
        row = BpReading(
            recorded_at=date, systolic=int(value["sys"]), diastolic=int(value["dia"]),
            pulse=int(value["pulse"]) if value.get("pulse") is not None else None,
            source="report", source_report_id=document_id, idempotency_key=key,
        )
    elif metric == "glucose":
        row = GlucoseReading(
            recorded_at=date, value=float(value["value"]), unit=str(value["unit"]),
            reading_type=str(value["reading_type"]),
            source="report", source_report_id=document_id, idempotency_key=key,
        )
    else:
        return None
    s.add(row)
    s.flush()
    return (row.__tablename__, row.id)
