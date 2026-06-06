"""ask — the persistent ask-anything assistant (PRD-16).

The connective tissue: a broad-read session that grounds answers in the user's
own rows (via read tools mirroring the UI RPCs) plus general pregnancy knowledge,
always with the §6 safety framing. **Read-only by design** — the allowlist has no
write tools, so Ask can never silently log medical data (§7). It reuses
``byo.session.*`` (no RPCs of its own).
"""

from __future__ import annotations

from pathlib import Path

from tinybeat_pregnancy.safety import with_safety
from byoh_bridge.workflows import Workflow
from .tools import register_tools

_HERE = Path(__file__).parent
_SKILL = with_safety((_HERE / "SKILL.md").read_text(encoding="utf-8"))


def build_workflow(ctx) -> Workflow:
    tools = register_tools(ctx)
    return Workflow(
        name="ask",
        skill=_SKILL,
        # Read tools only + the profile reader (owned by the profile workflow).
        # No write tools — Ask must not be able to log medical data.
        allowed_tools=[t.name for t in tools] + ["profile_get"],
    )
