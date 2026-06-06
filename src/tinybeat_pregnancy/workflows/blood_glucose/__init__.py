"""blood_glucose — log + chart glucose with fasting/post-meal context (PRD-11).

A standard metric module (the framework does the work): `glucose_log` via the
shared factory, `byo.glucose.list` for the dashboard. Glucose isn't a red-flag
domain (GDM is a provider diagnosis, never ours) — the SKILL frames everything as
"to discuss with your provider"; no safety-escalation fragment.
"""

from __future__ import annotations

from pathlib import Path

from byoh_bridge.workflows import Workflow
from .rpcs import collect_rpcs
from .tools import register_tools

_HERE = Path(__file__).parent
_SKILL = (_HERE / "SKILL.md").read_text(encoding="utf-8")


def build_workflow(ctx) -> Workflow:
    tools = register_tools(ctx)
    return Workflow(
        name="blood_glucose",
        skill=_SKILL,
        allowed_tools=[t.name for t in tools],
        rpcs=collect_rpcs(),
    )
