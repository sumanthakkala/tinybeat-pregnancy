"""glucose_log — record one blood-glucose reading (PRD-11).

Built from the shared metric factory (PRD-05). The ``reading_type`` + ``unit``
are constrained to enums (they select the target band, so a wrong value would
mis-chart). No special write logic — out-of-target framing is display-side + in
the SKILL.
"""

from __future__ import annotations

from tinybeat_pregnancy.storage.models.glucose_reading import GlucoseReading
from byoh_bridge.workflows import Field, make_log_tool

TOOL = make_log_tool(
    name="glucose_log",
    model=GlucoseReading,
    fields=[
        Field("value", "number", "The glucose value (in the given unit)."),
        Field("unit", "string", "Unit of the value.", enum=("mg/dL", "mmol/L")),
        Field(
            "reading_type",
            "string",
            "Context of the reading — this selects the target band.",
            enum=("fasting", "post_meal_1h", "post_meal_2h", "random"),
        ),
        Field("meal", "string", "What was eaten (for a post-meal reading).", required=False),
    ],
    description=(
        "Record one blood-glucose reading to the user's local tracker. Use only when "
        "the user gives a value (e.g. 'fasting 92', '1-hour 142'). Default unit to "
        "mg/dL if not stated, but ask once if it's truly unclear. Map context to "
        "reading_type: 'fasting' | 'post_meal_1h' | 'post_meal_2h' | 'random'. ALWAYS "
        "supply a stable idempotency_key like 'manual:2026-06-05:fasting:92'. Re-runs "
        "with the same key are no-ops. If a value is above the usual target for its "
        "type, gently note it as general info to discuss with their provider — never a "
        "diagnosis of gestational diabetes."
    ),
    emoji="🩸",
)
