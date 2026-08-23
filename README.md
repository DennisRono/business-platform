# Business Platform API

Production-grade FastAPI backend scaffold with a strict layered architecture,
async SQLAlchemy 2.0 + Postgres, JWT auth, RBAC, rate limiting, structured
logging, Alembic migrations, Docker/Kubernetes manifests, and CI/CD.

## Architecture

Requests flow through thin layers, each with a single responsibility:

```
HTTP  ─▶  endpoint  ─▶  controller  ─▶  service  ─▶  model (ORM)
             │              │             │
          schema        business       cross-cutting
        (validation)     rules /        helpers /
                         DB access       integrations
```

- **endpoints** (`app/api/endpoints/`) — HTTP surface only: routing, status
  codes, dependency injection, request/response schemas. No business logic.
- **controllers** (`business_platform/controllers/`) — the ONLY layer that
  touches the ORM/session. Business rules, transactions, soft deletes.
- **services** (`business_platform/services/`) — reusable cross-cutting logic
  (tokens, external integrations) with no direct HTTP coupling.
- **models** (`business_platform/models/`) — SQLAlchemy declarative models. All
  models are re-exported from `models/__init__.py` so Alembic autogenerate and
  `Base.metadata` see them.
- **schemas** (`business_platform/schemas/`) — Pydantic v2 request/response DTOs.
- **core** (`business_platform/core/`) — config, security, logging, exceptions.
- **middleware** (`business_platform/middleware/`) — security headers, rate
  limiting, permission checks, audit logging.

The **users** domain is wired end-to-end as the reference implementation to copy
when adding new domains.

## Quick start (local, Docker)

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- Interactive docs (RapiDoc): http://localhost:8000/docs
- Swagger UI: http://localhost:8000/swagger
- OpenAPI JSON: http://localhost:8000/openapi.json

## Quick start (local, Poetry)

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

## Common tasks

```bash
make run        # run the dev server
make migrate    # alembic upgrade head
make revision m="add widgets table"   # autogenerate a migration
make test       # run the test suite
make lint       # ruff + mypy
make seed       # seed default roles/permissions
```

## Adding a new domain

1. `business_platform/models/<domain>.py` — the ORM model, then re-export it in
   `business_platform/models/__init__.py`.
2. `business_platform/schemas/<domain>.py` — Pydantic DTOs.
3. `business_platform/controllers/<domain>.py` — DB access + business rules.
4. `business_platform/services/<domain>.py` — optional cross-cutting logic.
5. `app/api/endpoints/<domain>.py` — the router; include it in
   `app/api/routes.py`.
6. `alembic revision --autogenerate -m "add <domain>"`.

## Deployment

- **Docker**: `Dockerfile` (API) and `Dockerfile.worker` (background worker).
- **Kubernetes**: `k8s/` (namespace, config, secrets, RBAC, deployment,
  service, ingress, HPA, PDB). Applied in order by filename.
- **CI** (`.github/workflows/ci.yml`): lint, type-check, migrate, test.
- **CD** (`.github/workflows/cd.yml`): build/push images on tags, deploy to k8s.
