"""Symptom taxonomy (PRD-12) — the canonical key set the agent logs against.

Mirrored on the FE in ``app/lib/symptoms/taxonomy.ts`` (labels/categories for the
chips) and ``app/lib/guidance/redflags.ts`` (the red-flag predicate). The
``red_flag`` keys here MUST match ``redflags.ts`` so the agent and the UI agree on
what's serious. Keep the three in sync.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Symptom:
    key: str
    label: str
    category: str  # common | aches_body | red_flag
    red_flag: bool = False


# Order is the display order within each category.
_SYMPTOMS: tuple[Symptom, ...] = (
    # ── Common ──────────────────────────────────────────────────────────────
    Symptom("nausea", "Nausea", "common"),
    Symptom("vomiting", "Vomiting", "common"),
    Symptom("heartburn", "Heartburn", "common"),
    Symptom("constipation", "Constipation", "common"),
    Symptom("fatigue", "Fatigue", "common"),
    Symptom("insomnia", "Trouble sleeping", "common"),
    Symptom("dizziness", "Dizziness", "common"),
    Symptom("headache", "Headache (mild)", "common"),
    Symptom("congestion", "Congestion", "common"),
    Symptom("mood_low", "Low mood", "common"),
    # ── Aches & body ────────────────────────────────────────────────────────
    Symptom("back_pain", "Back pain", "aches_body"),
    Symptom("cramping", "Cramping (mild)", "aches_body"),
    Symptom("pelvic_pressure", "Pelvic pressure", "aches_body"),
    Symptom("swelling", "Swelling (mild)", "aches_body"),
    Symptom("shortness_of_breath", "Shortness of breath", "aches_body"),
    # ── Worth a call (red-flags — mirror redflags.ts) ───────────────────────
    Symptom("bleeding", "Vaginal bleeding", "red_flag", True),
    Symptom("bleeding_heavy", "Heavy bleeding", "red_flag", True),
    Symptom("abdominal_pain_severe", "Severe abdominal pain", "red_flag", True),
    Symptom("reduced_fetal_movement", "Reduced baby movement", "red_flag", True),
    Symptom("headache_severe", "Severe / persistent headache", "red_flag", True),
    Symptom("vision_changes", "Vision changes", "red_flag", True),
    Symptom("fever", "Fever", "red_flag", True),
    Symptom("contractions_regular", "Regular contractions", "red_flag", True),
    Symptom("fluid_leak", "Leaking fluid", "red_flag", True),
    Symptom("chest_pain", "Chest pain", "red_flag", True),
    Symptom("trouble_breathing", "Trouble breathing", "red_flag", True),
    Symptom("fainting", "Fainting", "red_flag", True),
    Symptom("seizure", "Seizure", "red_flag", True),
    Symptom("swelling_sudden", "Sudden swelling", "red_flag", True),
)

SYMPTOMS: dict[str, Symptom] = {s.key: s for s in _SYMPTOMS}
KEYS: frozenset[str] = frozenset(SYMPTOMS)
RED_FLAG_KEYS: frozenset[str] = frozenset(k for k, s in SYMPTOMS.items() if s.red_flag)


def is_valid(key: str) -> bool:
    return key in SYMPTOMS


def is_red_flag(key: str) -> bool:
    s = SYMPTOMS.get(key)
    return bool(s and s.red_flag)


def label_of(key: str) -> str:
    s = SYMPTOMS.get(key)
    return s.label if s else key


def taxonomy_reference() -> str:
    """A compact key → label list for the SKILL (so it maps text to keys reliably)."""
    common = ", ".join(f"{s.key} ({s.label})" for s in _SYMPTOMS if not s.red_flag)
    flags = ", ".join(f"{s.key} ({s.label})" for s in _SYMPTOMS if s.red_flag)
    return (
        "## Symptom taxonomy (map the user's words to these keys)\n\n"
        f"Common: {common}\n\n"
        f"Red-flag (🚩 — escalate per the safety guidance, and still log): {flags}\n"
    )
