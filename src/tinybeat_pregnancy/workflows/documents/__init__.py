"""documents — uploaded-file metadata (PRD-07).

Read-only RPCs for the UI; the ``documents`` model is global; the actual file
transport (byo.file.upload_*/process) lives in the bridge. PRD-13 (extraction)
and PRD-42 (library) extend this workflow with classify/summarize tools.
"""

from __future__ import annotations

from byoh_bridge.workflows import Workflow
from .rpcs import collect_rpcs


def build_workflow(ctx) -> Workflow:
    return Workflow(name="documents", rpcs=collect_rpcs(), allowed_tools=[])
