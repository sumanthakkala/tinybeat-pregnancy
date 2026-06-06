"""tinybeat-pregnancy — the pregnancy domain plugin on top of byoh-bridge.

All the reusable machinery (relay dialer, tool sandbox, workflow/RPC
autodiscovery, SQLite storage engine, migration runner) lives in
``byoh_bridge``. This package contributes only the *domain*: the pregnancy
workflows, the ORM models, the shared safety fragment, and the Alembic history.

The whole wiring is one :class:`AppConfig` handed to :func:`byoh_bridge.register`.
"""

from __future__ import annotations

from byoh_bridge import AppConfig, session
from byoh_bridge import register as byoh_register

from .storage.models.document import Document

__version__ = "0.1.0"


class PregnancyDocumentStore:
    """How uploaded files become :class:`Document` rows (the one domain seam).

    The generic byoh-bridge upload pipeline streams bytes into the local inbox
    and hands us the committed metadata; we persist the domain-specific row.
    """

    def on_committed(self, s, meta: dict, params: dict) -> str:
        s.add(
            Document(
                id=meta["inbox_id"],
                filename=meta["filename"],
                mime=meta["mime"],
                size_bytes=meta["size_bytes"],
                sha256=meta["sha256"],
                inbox_path=meta["path"],
                kind=str(params.get("kind") or "other"),
                status="received",
            )
        )
        return meta["inbox_id"]

    def resolve(self, doc_id: str):
        with session() as s:
            d = s.get(Document, doc_id)
            return {"path": d.inbox_path, "mime": d.mime} if d else None

    def set_status(self, s, doc_id: str, status: str) -> None:
        d = s.get(Document, doc_id)
        if d:
            d.status = status


APP_CONFIG = AppConfig(
    name="tinybeat-pregnancy",
    workflows_package="tinybeat_pregnancy.workflows",
    models_package="tinybeat_pregnancy.storage.models",
    migrations_path=__path__[0] + "/alembic",
    document_store=PregnancyDocumentStore(),
)


def register(ctx):
    """Hermes plugin entrypoint — hand our AppConfig to the bridge."""
    byoh_register(ctx, APP_CONFIG)
