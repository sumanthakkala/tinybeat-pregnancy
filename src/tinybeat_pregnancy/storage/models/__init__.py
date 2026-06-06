"""Centralized ORM models for the byo-pregnancy-bridge plugin.

**Why here and not per-workflow:** schema is fundamentally global.
ForeignKey + relationship() cross feature boundaries (a checklist
question references an appointment id; a journey-timeline event
references rows across many tables). Putting all model classes in one
flat namespace means:

- One ``Base.metadata`` — Alembic compares it to the live DB.
- ForeignKey references work without cross-workflow imports.
- One predictable place to look for the schema definition.

Workflows still own *behavior* (tools/, rpcs/, SKILL.md). They consume
models via:

    from tinybeat_pregnancy.storage.models.weight_log import WeightLog

This package's ``__init__.py`` autodiscovers every non-underscore-
prefixed ``.py`` file and imports it for side effects (model classes
register themselves with ``Base.metadata`` via SQLAlchemy's
declarative magic).

**Adding a new model:** drop a new ``<name>.py`` file here with a
class inheriting from ``..base.Base``. Then run
``alembic revision --autogenerate -m "..."`` to generate the migration.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil

logger = logging.getLogger(__name__)


def discover_models() -> list[str]:
    """Import every model module so classes register with Base.metadata.

    Returns the list of module names imported. Underscore-prefixed
    files (e.g. ``_mixins.py``) are skipped.
    """
    imported: list[str] = []
    pkg = importlib.import_module(__name__)
    for mod_info in pkgutil.iter_modules(pkg.__path__):
        if mod_info.name.startswith("_"):
            continue
        full = f"{__name__}.{mod_info.name}"
        try:
            importlib.import_module(full)
        except Exception as exc:
            logger.exception("[models] failed to import %s: %s", mod_info.name, exc)
            continue
        imported.append(mod_info.name)
    return imported


# Eager discovery at package-import time so ``Base.metadata`` is fully
# populated whenever anything imports ``storage`` (which happens before
# Alembic runs, before the first ORM query, etc.). Order-independent —
# callers don't need to know discover_models() exists.
discover_models()
