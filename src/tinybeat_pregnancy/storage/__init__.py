"""Storage facade — the shared SQLite layer lives in ``byoh_bridge``.

This plugin owns only its domain *models* (``tinybeat_pregnancy.storage.models``).
The engine, session factory, declarative ``Base``, change-events, and migration
runner all come from the framework; we re-export the common handles here so
domain code can keep importing them from one predictable place.
"""

from byoh_bridge.storage import Base, db_path, session  # noqa: F401 — re-export

__all__ = ["Base", "db_path", "session"]
