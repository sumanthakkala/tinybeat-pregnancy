"""appointments — the logistics backbone of Care (PRD-14).

Create/edit/cancel visits and attach follow-up notes. Pure logistics (no
diagnostic content), so no safety fragment — the detail view links out to the
care team (PRD-17/18). The checklist (PRD-15) and questions/debrief (PRD-19)
hang off ``appointment_id`` and read context via the ``appointment_get`` tool.
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
        name="appointments",
        skill=_SKILL,
        allowed_tools=[t.name for t in tools],
        rpcs=collect_rpcs(),
    )
