"""report_extraction — the passive-ingestion magic moment (PRD-13).

Driven by ``byo.file.process{workflow:"report_extraction"}``: a *scoped* session
(PRD-06) reads an uploaded report and proposes values into the ``extracted_values``
staging table — it never writes a metric row directly (§6.3). The user confirms
each via ``byo.report.confirm``, which writes the real metric row with
``source="report"`` provenance.

The session's allowlist = the report tools **plus** the agent's file-reading
tools (so it can open the PDF/image) — and crucially *not* the metric write tools
(``weight_log`` etc.), so the agent can't bypass staging. Read-tool names below
match a standard Hermes build; adjust if a deployment renames them.
"""

from __future__ import annotations

from pathlib import Path

from tinybeat_pregnancy.safety import with_safety
from byoh_bridge.workflows import Workflow
from .rpcs import collect_rpcs
from .tools import register_tools

_HERE = Path(__file__).parent
_SKILL = with_safety((_HERE / "SKILL.md").read_text(encoding="utf-8"))

# Native read tools the agent needs to open the uploaded file. Deliberately
# excludes the metric write tools so staging can't be bypassed.
_READ_TOOLS = ["bash", "read_file"]


def build_workflow(ctx) -> Workflow:
    tools = register_tools(ctx)
    return Workflow(
        name="report_extraction",
        skill=_SKILL,
        allowed_tools=[t.name for t in tools] + _READ_TOOLS,
        rpcs=collect_rpcs(),
    )
