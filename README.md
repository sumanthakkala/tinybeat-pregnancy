# tinybeat-pregnancy

The pregnancy **domain** plugin for a BYOH ("agent-as-backend") app. All the
reusable machinery — the outbound relay dialer, the per-session tool sandbox,
typed-tool / RPC autodiscovery, the local-SQLite storage engine with automatic
change-events, and the migration runner — lives in the
[`byoh-bridge`](https://github.com/sumanthakkala/byoh-bridge) framework. This
package contributes only the domain:

- **11 workflows** (`src/tinybeat_pregnancy/workflows/`): weight logging, blood
  pressure, blood glucose, symptoms, appointments, appointment checklist, report
  extraction, ask, profile, journey, documents.
- **11 ORM models** (`src/tinybeat_pregnancy/storage/models/`) on the shared
  `byoh_bridge.storage.Base`.
- the shared **safety fragment** (`src/tinybeat_pregnancy/safety/`).
- the **Alembic history** (`src/tinybeat_pregnancy/alembic/versions/`).

The whole plugin is wired by one `AppConfig` in
`src/tinybeat_pregnancy/__init__.py`.

## Install into Hermes (and why it takes two steps)

> ### The gotcha: flat-dir loader vs. pip package
> **Problem.** Hermes (≤ 0.15.x) discovers plugins as **flat directories** and
> loads the plugin's **root `__init__.py` by path** (as
> `hermes_plugins.tinybeat_pregnancy`), then calls `register(ctx)`. It does
> **not** `pip install` the plugin or add its deps.
>
> **Why that breaks a clean `hermes plugins install` here.** This project is a
> **src-layout pip package** (`src/tinybeat_pregnancy/`) whose code refers to
> itself by the absolute import name `tinybeat_pregnancy` (in
> `AppConfig.models_package`, the Alembic `env.py`, etc.) and depends on
> `byoh-bridge`. So a bare clone doesn't run: Hermes finds **no `register()` at
> the directory root**, and `import tinybeat_pregnancy` / `import byoh_bridge`
> **fail** because nothing was installed into Hermes's venv.
>
> **The solution (two parts).**
> 1. A tiny **root `__init__.py` shim** (committed at the repo root):
>    `from tinybeat_pregnancy import register` — gives Hermes's path-loader the
>    `register(ctx)` it expects, delegating to the real package.
> 2. A **`pip install`** of the package into Hermes's venv so `tinybeat_pregnancy`
>    resolves and `byoh-bridge` (+ SQLAlchemy/Alembic/websockets) are pulled in.
>
> This is the "entry-point / package plugin discovery" gap tracked in the
> framework's [`docs/byoh/03-HERMES-GAPS.md`](https://github.com/sumanthakkala/byoh-bridge).
> When Hermes can load installed packages directly, **both the shim and the
> manual pip step go away** — `hermes plugins install` alone will suffice.

```bash
# 1) clone into Hermes's plugin dir (native installer)
hermes --profile <profile> plugins install sumanthakkala/tinybeat-pregnancy --no-enable

# 2) pip-install the clone into Hermes's venv so the package + byoh-bridge resolve.
#    (byoh-bridge currently lives on TestPyPI; once it's on PyPI, plain `pip install <dir>` works.)
~/.hermes/hermes-agent/venv/bin/pip install \
  -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ \
  ~/.hermes/profiles/<profile>/plugins/tinybeat-pregnancy

# 3) enable + restart
hermes --profile <profile> plugins enable tinybeat-pregnancy
hermes --profile <profile> gateway restart
```

**Local development** instead wants editable installs so edits are live:

```bash
git clone https://github.com/sumanthakkala/tinybeat-pregnancy && cd tinybeat-pregnancy
~/.hermes/hermes-agent/venv/bin/pip install -e ../byoh-bridge   # editable framework
~/.hermes/hermes-agent/venv/bin/pip install -e .                # editable plugin
ln -s "$PWD" ~/.hermes/profiles/<dev-profile>/plugins/tinybeat-pregnancy
hermes --profile <dev-profile> plugins enable tinybeat-pregnancy
# edit → `hermes --profile <dev-profile> gateway restart` → test
```

On startup Hermes calls `register(ctx)` (root shim → `tinybeat_pregnancy.register`),
which hands `APP_CONFIG` to `byoh_bridge.register`: workflows/tools/RPCs are
autodiscovered and the SQLite schema is migrated to head automatically.

## Configuration (`BYOH_*` env vars)

All resolved from `AppConfig` with env overrides:

| Variable             | Default                                   | Purpose                                  |
| -------------------- | ----------------------------------------- | ---------------------------------------- |
| `BYOH_DATA_DIR`      | `<hermes_home>/tinybeat-pregnancy`        | data dir for `app.db` + the upload inbox |
| `BYOH_RELAY_URL`     | `ws://127.0.0.1:3000/ws/agent`            | outbound relay websocket                 |
| `BYOH_AGENT_ID`      | `tinybeat-pregnancy-local`                | agent identity on the relay              |
| `BYOH_BRIDGE_ENABLED`| `true`                                    | set `0`/`false` to skip the relay dialer |

## Migrations

The app owns its `versions/`. `env.py` is a 3-liner that hands `APP_CONFIG` to
`byoh_bridge.alembic_support.run_env`; the DB URL is derived at runtime from the
active config, so the bare CLI works:

```bash
export BYOH_DATA_DIR=$(mktemp -d)
~/.hermes/hermes-agent/venv/bin/alembic upgrade head      # builds all 11 tables
~/.hermes/hermes-agent/venv/bin/alembic revision --autogenerate -m "..."   # add a model, then this
```

## Layout

```
src/tinybeat_pregnancy/
  __init__.py            # APP_CONFIG + PregnancyDocumentStore + register(ctx)
  workflows/<wf>/        # tools/ + rpcs/ (3-line shims) + SKILL.md per workflow
  storage/models/        # the 11 domain models (subclass byoh_bridge Base)
  safety/                # _safety.py + _safety.md (shared escalate-don't-diagnose copy)
  alembic/               # env.py + script.py.mako + versions/
```
