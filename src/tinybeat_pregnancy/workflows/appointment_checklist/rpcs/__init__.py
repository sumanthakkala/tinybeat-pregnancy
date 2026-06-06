"""RPC autodiscovery shim — delegates to the framework.

Drop a ``<name>.py`` exporting ``RPC = Rpc(...)`` here; ``build_workflow``
picks it up via ``collect_rpcs()``. ``_``-prefixed files are skipped.
"""

from byoh_bridge.workflows import collect_rpcs as _collect_rpcs


def collect_rpcs():
    return _collect_rpcs(__name__)
