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

## Install

```bash
git clone https://github.com/sumanthakkala/tinybeat-pregnancy
cd tinybeat-pregnancy
~/.hermes/hermes-agent/venv/bin/pip install -e .      # pulls in byoh-bridge
```

## Make Hermes discover it

Symlink (or copy) the repo into your Hermes profile's plugins directory and
enable it:

```bash
ln -s "$PWD" ~/.hermes/profiles/<profile>/plugins/tinybeat-pregnancy
```

Then add it to the profile's `plugins.enabled` list. Hermes calls
`tinybeat_pregnancy.register(ctx)` at startup, which hands `APP_CONFIG` to
`byoh_bridge.register` — workflows/tools/RPCs are discovered and the SQLite
schema is migrated to head automatically.

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
