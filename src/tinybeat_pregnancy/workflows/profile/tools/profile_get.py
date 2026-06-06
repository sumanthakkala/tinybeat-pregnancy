"""profile_get — agent-read tool: the user's profile + current gestational week.

Lets agents (digest, guidance, ask, checklist) ground answers in the user's
stage and preferences. Read-only; never writes.
"""

from __future__ import annotations

import json
from typing import Any

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.profile import Profile
from byoh_bridge.workflows import Tool
from .._serialize import profile_to_dict
from .._week import gestation_for_profile

SCHEMA: dict = {
    "name": "profile_get",
    "description": (
        "Read the user's pregnancy profile (name, due date, current gestational week, "
        "units) to ground your guidance in their context. Read-only — never changes anything."
    ),
    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
}


def handler(_args: dict[str, Any], **_: Any) -> str:
    with storage.session() as s:
        p = s.get(Profile, 1)
        prof = profile_to_dict(p) if p else None
    gest = gestation_for_profile(prof) if prof else None
    return json.dumps({"ok": True, "profile": prof, "gestation": gest})


TOOL = Tool(
    name="profile_get",
    toolset="hermes-cli",
    schema=SCHEMA,
    handler=handler,
    description="Read the user's pregnancy profile + current week (read-only).",
    emoji="🤰",
)
