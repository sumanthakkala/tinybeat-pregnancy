"""journey — the scroll-driven dashboard's data layer (PRD-08).

Read-only, render-mode: a single aggregation RPC (``byo.journey.overlay``) that
denormalizes the user's real rows from across the other feature tables into a
week-keyed structure, so the Journey can dock "memory cards" to the weeks the
user has lived **without the UI fanning out N queries**.

No tables, no tools, no SKILL — it owns nothing; it only *reads* what other
workflows write (weight today; bp/glucose/symptoms/appointments/reports/photos/
journal/kicks as those PRDs land). Like ``documents``, it's pure RPCs.
"""

from __future__ import annotations

from byoh_bridge.workflows import Workflow
from .rpcs import collect_rpcs


def build_workflow(ctx) -> Workflow:
    return Workflow(name="journey", rpcs=collect_rpcs(), allowed_tools=[])
