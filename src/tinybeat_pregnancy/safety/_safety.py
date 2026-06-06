"""Shared safety fragment loader (PRD-17).

The canonical safety language lives in ``_safety.md`` so it can be reviewed and
updated in one place. Medical workflows fold it into their SKILL via
``with_safety()`` in ``build_workflow`` so the agent's escalate-don't-diagnose
behavior is consistent everywhere. The FE ``redflags.ts`` predicate is the
deterministic backstop; this is the prose side.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_SAFETY_PATH = Path(__file__).parent / "_safety.md"


@lru_cache(maxsize=1)
def safety_fragment() -> str:
    """The shared safety SKILL text (cached)."""
    return _SAFETY_PATH.read_text(encoding="utf-8").strip()


def with_safety(skill: str) -> str:
    """Prepend the shared safety fragment to a workflow's SKILL text.

    Safety leads so it's never buried under task instructions. Medical workflows
    call this in ``build_workflow``::

        skill = with_safety((HERE / "SKILL.md").read_text())
    """
    return f"{safety_fragment()}\n\n---\n\n{skill.strip()}\n"
