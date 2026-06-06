"""weight_logging — first reference workflow.

Wires together the *behavior* artifacts:
- ``tools/`` — one file per tool (autodiscovered)
- ``rpcs/``  — one file per RPC (autodiscovered)
- ``SKILL.md`` — instructions injected into the first prompt

**Schema models live globally** at ``storage/models/`` (see
``docs/POC-IMPLEMENTATION.md`` §4.3). The tools and RPCs in this
workflow import models from there. Schema migrations are managed by
Alembic globally under ``<plugin>/alembic/versions/``.
"""

from __future__ import annotations

from pathlib import Path

from byoh_bridge.workflows import Workflow
from .rpcs import collect_rpcs
from .tools import register_tools

_HERE = Path(__file__).parent
_SKILL = (_HERE / "SKILL.md").read_text(encoding="utf-8")


def build_workflow(ctx) -> Workflow:
    # Autodiscover tools/ and rpcs/ — adding either is just dropping
    # a new file in the matching directory.
    tools = register_tools(ctx)
    return Workflow(
        name="weight_logging",
        skill=_SKILL,
        allowed_tools=[t.name for t in tools],   # derived — can't drift
        rpcs=collect_rpcs(),
    )
