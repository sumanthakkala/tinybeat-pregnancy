"""byo.profile.set — upsert the single-row profile.

The ONE sanctioned write RPC in the codebase: profile fields are deterministic
user input (no extraction), so they don't need an agent tool. All medical writes
still go through agent tools. Partial — only provided, non-null fields are set,
so updating `due_date` alone never wipes `name`.
"""

from __future__ import annotations

from byoh_bridge import storage
from tinybeat_pregnancy.storage.models.profile import Profile
from byoh_bridge.workflows import Rpc
from .._serialize import profile_to_dict

_FIELDS = {
    "name",
    "due_date",
    "lmp_date",
    "edd_source",
    "prepreg_weight_kg",
    "height_cm",
    "units_weight",
    "units_length",
    "birth_date",
    "postpartum",
}


def handler(params: dict) -> dict:
    with storage.session() as s:
        p = s.get(Profile, 1)
        if p is None:
            p = Profile(id=1, units_weight="kg", units_length="cm")
            s.add(p)

        for key in _FIELDS:
            if key in params and params[key] is not None:
                setattr(p, key, params[key])

        ec = params.get("emergency_contact")
        if isinstance(ec, dict):
            if ec.get("name") is not None:
                p.emergency_contact_name = ec["name"]
            if ec.get("phone") is not None:
                p.emergency_contact_phone = ec["phone"]

        s.flush()
        result = profile_to_dict(p)

    return {"profile": result}


RPC = Rpc(
    method="byo.profile.set",
    handler=handler,
    description="Upsert the single-row profile (deterministic user data).",
    read_only=False,
)
