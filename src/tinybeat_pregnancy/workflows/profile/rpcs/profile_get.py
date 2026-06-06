"""byo.profile.get — fetch the single-row profile for the UI."""

from __future__ import annotations

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.profile import Profile
from byoh_bridge.workflows import Rpc
from .._serialize import profile_to_dict


def handler(_params: dict) -> dict:
    with storage.session() as s:
        p = s.get(Profile, 1)
        return {"profile": profile_to_dict(p) if p else None}


RPC = Rpc(
    method="byo.profile.get",
    handler=handler,
    description="Return the single-row profile (or null).",
    read_only=True,
)
