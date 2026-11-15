# WBS-13.1 — Dummy University REST API

This is a **fictional**, standalone FastAPI service and seed dataset for use by the
SynapseITU University Data Agent (WBS-13.2). It does not connect to any real university.

## Start locally

From the repository root:

```bash
# Main API on :8000, dummy university on :8001
docker compose -f compose.dummy-university.yml up --build
```

The dummy university's Swagger UI is `http://localhost:8001/docs`.
The SynapseITU health endpoint remains `http://localhost:8000/health`.

The services talk to one another inside Docker using
`http://dummy-university:8000`.
This compose file demonstrates side-by-side operation locally; the team must
add the service to its real staging deployment (WBS-14.6).

## REST contract

| Endpoint | Description |
| --- | --- |
| `GET /health` | Liveness check |
| `GET /programs` and `GET /programs/{record_id}` | Seeded degree programs |
| `GET /labs` and `GET /labs/{record_id}` | Seeded research labs |
| `GET /positions` and `GET /positions/{record_id}` | Seeded research positions |
| `GET /openapi.json` | Machine-readable OpenAPI contract |

Responses have stable IDs, a fictional university ID, record details, an
`updated_at` timestamp, and an absolute `source_url` pointing to the same
record in the dummy service. `lab_id` and `program_id` connect positions to
related records. Unknown record IDs return HTTP 404. Lists are read-only.

## Tests / acceptance

From repo root, run:

```bash
cd backend
uv sync --locked --all-groups
uv run --locked ruff check . ../tests/backend
uv run --locked ruff format --check . ../tests/backend
uv run --locked python -m pytest -q
```

The WBS-13.1 contract tests live in
`tests/backend/unit/test_dummy_university.py`. The Docker CI test stage also
runs them automatically. Deployment to **staging** requires the DevOps owner
to add the service to the staging environment; this example only proves local
container interoperability.
