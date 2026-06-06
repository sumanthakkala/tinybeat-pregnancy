"""Tool autodiscovery shim — delegates to the framework.

Drop a ``<name>.py`` exporting ``TOOL = Tool(...)`` here; ``build_workflow``
picks it up via ``register_tools(ctx)``. ``_``-prefixed files are skipped.
"""

from byoh_bridge.workflows import register_tools as _register_tools


def register_tools(ctx):
    return _register_tools(ctx, __name__)
