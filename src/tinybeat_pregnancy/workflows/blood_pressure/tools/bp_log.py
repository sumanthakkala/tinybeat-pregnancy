"""bp_log — record one blood-pressure reading (PRD-10).

Built from the shared metric factory (PRD-05): the common
``{recorded_at, <values…>, note?, source?, idempotency_key}`` → idempotent
insert shape. BP needs no special write logic (the red-flag handling is
display-side + in the SKILL), so the factory is the right fit.
"""

from __future__ import annotations

from tinybeat_pregnancy.storage.models.bp_reading import BpReading
from byoh_bridge.workflows import Field, make_log_tool

TOOL = make_log_tool(
    name="bp_log",
    model=BpReading,
    fields=[
        Field("systolic", "integer", "Systolic (top number), mmHg. 70–250."),
        Field("diastolic", "integer", "Diastolic (bottom number), mmHg. 40–150."),
        Field("pulse", "integer", "Heart rate in bpm (optional).", required=False),
        Field("arm", "string", "Which arm: left | right (optional).", required=False),
        Field("position", "string", "Body position: sitting | lying | standing (optional).", required=False),
    ],
    description=(
        "Record one blood-pressure reading to the user's local tracker. Use only "
        "when the user gives a reading (e.g. 'BP 118/76'). ALWAYS supply a stable "
        "idempotency_key like 'manual:2026-06-05:118/76'. Re-runs with the same key "
        "are no-ops. After logging, if systolic ≥140 or diastolic ≥90, gently note "
        "that it's higher than the typical range and suggest contacting their provider."
    ),
    emoji="🩺",
)
