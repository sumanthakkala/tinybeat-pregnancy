"""blood_pressure — log + chart BP, red-flag aware (PRD-10).

The first metric where the safety layer is the point: hypertensive readings route
to the preeclampsia-aware escalation (PRD-17). This workflow is the **first
consumer of the shared safety fragment** — ``with_safety`` folds the canonical
guide-don't-diagnose + red-flag language ahead of the BP-specific SKILL.
"""

from __future__ import annotations

from pathlib import Path

from tinybeat_pregnancy.safety import with_safety
from byoh_bridge.workflows import Workflow
from .rpcs import collect_rpcs
from .tools import register_tools

_HERE = Path(__file__).parent
_SKILL = with_safety((_HERE / "SKILL.md").read_text(encoding="utf-8"))


def build_workflow(ctx) -> Workflow:
    tools = register_tools(ctx)
    return Workflow(
        name="blood_pressure",
        skill=_SKILL,
        allowed_tools=[t.name for t in tools],
        rpcs=collect_rpcs(),
    )
