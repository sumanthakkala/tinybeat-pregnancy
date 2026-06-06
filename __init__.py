"""Hermes plugin entry point — flat-directory loader shim.

Hermes (≤ 0.15.x) discovers plugins as **flat directories** and loads this
top-level ``__init__.py`` *by path* (as ``hermes_plugins.tinybeat_pregnancy``),
then calls ``register(ctx)``. But this project is a **src-layout pip package**
(`src/tinybeat_pregnancy/`) whose code self-references the absolute import name
``tinybeat_pregnancy`` (in ``AppConfig.models_package``, the Alembic env, etc.).

So the two worlds are bridged here: Hermes loads this shim by path; the shim
delegates to the installed package. **This requires the package to be
pip-installed** (`pip install .`), which also pulls in ``byoh-bridge`` + its
deps. See the README → "Install into Hermes" for the exact steps and the
reason. When Hermes gains entry-point/package plugin discovery, this shim and
the manual pip step both go away.
"""

from tinybeat_pregnancy import APP_CONFIG, register  # noqa: F401
