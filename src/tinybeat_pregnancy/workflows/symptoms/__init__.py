"""symptoms — tagged symptom logging, red-flag aware (PRD-12).

A core safety surface: the agent classifies free text into the taxonomy, logs one
row per symptom/day, and escalates any red-flag (the FE re-checks via the shared
``redflags.ts`` so escalation never depends solely on the model). Uses the shared
safety fragment (``with_safety``).
"""

from __future__ import annotations

from pathlib import Path

from tinybeat_pregnancy.safety import with_safety
from byoh_bridge.workflows import Workflow
from ._taxonomy import taxonomy_reference
from .rpcs import collect_rpcs
from .tools import register_tools

_HERE = Path(__file__).parent
# Safety leads; then the symptom instructions; then the live taxonomy key list
# (kept in sync with _taxonomy.py automatically).
_SKILL = with_safety(
    (_HERE / "SKILL.md").read_text(encoding="utf-8") + "\n\n" + taxonomy_reference()
)


def build_workflow(ctx) -> Workflow:
    tools = register_tools(ctx)
    return Workflow(
        name="symptoms",
        skill=_SKILL,
        allowed_tools=[t.name for t in tools],
        rpcs=collect_rpcs(),
    )
