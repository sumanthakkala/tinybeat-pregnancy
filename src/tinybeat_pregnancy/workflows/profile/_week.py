"""Gestational-week engine — Python mirror of ``app/lib/pregnancy/week.ts`` (PRD-03).

Keep in sync with the TS version so agents (digest, guidance) compute the same
week the UI shows. Pure stdlib; no Hermes deps.
"""

from __future__ import annotations

from datetime import date, timedelta

TERM_DAYS = 280
MAX_DAYS = 294  # 42w clamp ceiling


def _parse(iso: str) -> date:
    return date.fromisoformat(iso)


def days_between(a_iso: str, b_iso: str) -> int:
    """Whole days from a to b (b - a)."""
    return (_parse(b_iso) - _parse(a_iso)).days


def today_iso() -> str:
    return date.today().isoformat()


def add_days_iso(iso: str, days: int) -> str:
    return (_parse(iso) + timedelta(days=days)).isoformat()


def edd_from_lmp(lmp_iso: str) -> str:
    """EDD from last menstrual period (LMP + 280 days)."""
    return add_days_iso(lmp_iso, TERM_DAYS)


def gestation(due_iso: str, today: str) -> dict:
    """Gestational status from an estimated due date and 'today'."""
    days_until = days_between(today, due_iso)
    days = max(0, min(MAX_DAYS, TERM_DAYS - days_until))
    week = days // 7
    dow = days % 7
    trimester = 1 if week < 14 else 2 if week < 28 else 3
    return {
        "days": days,
        "week": week,
        "day_of_week": dow,
        "trimester": trimester,
        "weeks_to_go": max(0, 40 - week),
        "progress": min(1.0, max(0.0, days / TERM_DAYS)),
        "label": f"{week}w {dow}d",
    }


def gestation_for_profile(profile: dict, today: str | None = None) -> dict | None:
    """Compute gestation from a profile dict (due_date preferred, else lmp_date)."""
    today = today or today_iso()
    due = profile.get("due_date")
    if not due and profile.get("lmp_date"):
        due = edd_from_lmp(profile["lmp_date"])
    if not due:
        return None
    return gestation(due, today)
