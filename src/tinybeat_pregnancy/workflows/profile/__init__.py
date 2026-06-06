"""profile — the user's core facts + the gestational-week engine (PRD-03).

Mostly RPC-driven (``byo.profile.get`` / ``byo.profile.set``, the one sanctioned
write RPC). Exposes one agent-read tool, ``profile_get``, so other workflows can
ground guidance in the user's stage. The week math mirror lives in ``_week.py``.
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
        name="profile",
        skill=_SKILL,
        allowed_tools=[t.name for t in tools],
        rpcs=collect_rpcs(),
    )
