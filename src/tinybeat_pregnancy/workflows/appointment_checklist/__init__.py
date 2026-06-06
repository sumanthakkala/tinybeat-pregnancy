"""appointment_checklist — the flagship guided conversation (PRD-15).

The user clicks "Plan checklist" on an appointment; this scoped session
interviews them and writes one ``checklist_questions`` row per agreed item, which
appears live in the UI. Registered as **"checklist_builder"** (the name the UI
passes to ``byo.session.start``).

The allowlist includes ``appointment_get`` (a tool the *appointments* workflow
owns and registers) so the agent can load the visit's context — the read tool
lives with the workflow whose agent needs it (MASTER-PLAN §5.6). The PRD-06
``pre_tool_call`` hook enforces that this session can call ONLY these four tools —
ask it to log a weight and it's blocked.
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
        name="checklist_builder",
        skill=_SKILL,
        # Own tools + the appointments read tool (registered by that workflow).
        allowed_tools=[t.name for t in tools] + ["appointment_get"],
        rpcs=collect_rpcs(),
    )
