"""Shared safety fragment (PRD-17) — re-exported for workflow SKILLs.

Medical workflows fold the canonical safety language into their SKILL via
``with_safety()`` so the escalate-don't-diagnose framing is consistent. The
prose lives in ``_safety.md``; the loader is in ``_safety.py``.
"""

from ._safety import safety_fragment, with_safety

__all__ = ["safety_fragment", "with_safety"]
