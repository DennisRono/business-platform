# Business Platform API

Businesses management API

## Architecture

Requests flow through thin layers, each with a single responsibility:

```text
HTTP  ─▶  endpoint  ─▶  controller  ─▶  service  ─▶  model (ORM)
             │              │             │
          schema        business       cross-cutting
        (validation)     rules /        helpers /
                         DB access       integrations
```

- **endpoints** (`app/api/endpoints/`) — HTTP surface only: routing, status codes, dependency injection, request/response schemas. No business logic.
- **controllers** (`business_platform/controllers/`) — the ONLY layer that touches the ORM/session. Business rules, transactions, soft deletes.
- **services** (`business_platform/services/`) — reusable cross-cutting logic (tokens, external integrations) with no direct HTTP coupling.
- **models** (`business_platform/models/`) — SQLAlchemy declarative models. All models are re-exported from `models/__init__.py` so Alembic autogenerate and `Base.metadata` see them.
- **schemas** (`business_platform/schemas/`) — Pydantic v2 request/response DTOs.
- **core** (`business_platform/core/`) — config, security, logging, exceptions.
- **middleware** (`business_platform/middleware/`) — security headers, rate limiting, permission checks, audit logging.

The **users** domain is wired end-to-end as the reference implementation to copy when adding new domains.

## Quick start with Docker

Docker Compose starts the complete local stack:

- FastAPI API
- PostgreSQL 16
- Redis 7
- Alembic migration job

### Prerequisites

Install Docker Desktop with Docker Compose support.

Verify the installation:

```bash
docker --version
docker compose version
```

### Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

For the Docker Compose environment, PostgreSQL is reached by its Compose service name, `db`, not `localhost`.

Your local `.env` should use values equivalent to:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-local-password
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_DB=business_platform
```

Inside Docker, use:

```text
db:5432
```

Do not use `localhost:5432` from the API or migration container. Inside a container, `localhost` refers to that container itself.

### Start the stack

```bash
docker compose up --build
```

Or with Make:

```bash
make up
```

The API will be available at:

- API: http://localhost:8000
- Interactive docs (RapiDoc): http://localhost:8000/docs
- Swagger UI: http://localhost:8000/swagger
- OpenAPI JSON: http://localhost:8000/openapi.json

### Run in detached mode

To start the stack in the background:

```bash
docker compose up --build -d
```

Or:

```bash
make docker-up
```

### Stop the stack

```bash
docker compose down
```

Or:

```bash
make down
```

### View API logs

```bash
docker compose logs -f api
```

Or:

```bash
make docker-logs
```

### View all service logs

```bash
docker compose logs -f
```

### Restart the stack

```bash
docker compose down
docker compose up --build
```

Or:

```bash
make docker-restart
```

### Open a shell in the API container

```bash
docker compose exec api /bin/bash
```

Or:

```bash
make docker-shell
```

### Rebuild images

When the Dockerfile or dependency configuration changes:

```bash
docker compose build --no-cache
docker compose up
```

For a normal rebuild:

```bash
docker compose up --build
```

## Docker Compose services

The local Compose stack contains four services:

```text
api
 ├── depends on migrate
 └── connects to db:5432 and redis:6379

migrate
 └── runs: alembic upgrade head

db
 └── PostgreSQL 16

redis
 └── Redis 7
```

The `migrate` service runs:

```bash
alembic upgrade head
```

The API waits for the migration job to complete successfully before starting.

Redis is available to containers at:

```text
redis://redis:6379/0
```

## PostgreSQL ports

If another PostgreSQL server is already running on your Mac on port `5432`, expose the Docker PostgreSQL server on a different host port.

Use:

```yaml
ports:
  - "5433:5432"
```

This means:

```text
Mac host                 Docker network

localhost:5433  ───────▶ db:5432
```

The port on the left is the Mac host port. The port on the right is the PostgreSQL container port.

The API and migration containers should continue using:

```text
db:5432
```

### Connecting with DBeaver

To connect to the Docker PostgreSQL instance from DBeaver:

```text
Host:     localhost
Port:     5433
Database: business_platform
Username: postgres
Password: <the value of POSTGRES_PASSWORD>
```

Do not use `db` as the hostname from DBeaver. `db` is the Docker Compose hostname and is available to containers on the Compose network.

## PostgreSQL data and volumes

PostgreSQL data is stored in the named Docker volume:

```text
pgdata
```

Normal shutdown does not remove the database data:

```bash
docker compose down
```

To completely remove the containers and PostgreSQL volume:

```bash
docker compose down -v
```

**Warning:** `docker compose down -v` deletes the local Docker PostgreSQL database and all data stored in it.

Use this when you intentionally want a clean local database, for example after changing the initial PostgreSQL credentials.

Then recreate the stack:

```bash
docker compose up --build
```

## Docker virtual environment and hot reload

The API image installs Poetry dependencies into:

```text
/app/.venv
```

The Dockerfile puts the virtual environment on `PATH`:

```text
/app/.venv/bin
```

For development, the API source is mounted into `/app` so Uvicorn can reload when source files change.

If your Compose file mounts:

```yaml
volumes:
  - ./:/app
```

also preserve the container virtual environment with:

```yaml
volumes:
  - ./:/app
  - /app/.venv
```

Without the second volume, the source-code mount can hide `/app/.venv`, causing errors such as:

```text
exec: "uvicorn": executable file not found in $PATH
```

The development API command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Common Docker commands

```bash
# Build and start the complete stack
make up

# Start in the background
make docker-up

# Stop containers
make down

# Build images
make docker-build

# Follow API logs
make docker-logs

# Restart the stack
make docker-restart

# Open a shell in the API container
make docker-shell

# Remove containers and PostgreSQL data
make docker-clean
```

Equivalent Docker Compose commands:

```bash
docker compose up --build
docker compose up --build -d
docker compose down
docker compose build
docker compose logs -f api
docker compose restart
docker compose exec api /bin/bash
docker compose down -v
```

## Database migrations with Docker

Migrations run automatically when the stack starts.

The Compose migration service executes:

```bash
alembic upgrade head
```

To run a migration manually:

```bash
docker compose run --rm migrate alembic upgrade head
```

To create a new migration, run Alembic from your Poetry environment:

```bash
poetry run alembic revision --autogenerate -m "add widgets table"
```

Then restart the Docker stack so the migration job applies it:

```bash
make up
```

## Quick start with Poetry

For development without Docker:

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

The local Poetry workflow expects PostgreSQL and Redis to be available outside the Docker network, so its environment configuration may differ from the Docker `.env` values.

## Common tasks

```bash
make run        # run the dev server
make migrate    # alembic upgrade head
make revision m="add widgets table"  # autogenerate a migration
make test       # run the test suite
make lint       # ruff + mypy
make seed       # seed default roles/permissions
```

## Adding a new domain

1. `business_platform/models/<domain>.py` — the ORM model, then re-export it in `business_platform/models/__init__.py`.
2. `business_platform/schemas/<domain>.py` — Pydantic DTOs.
3. `business_platform/controllers/<domain>.py` — DB access + business rules.
4. `business_platform/services/<domain>.py` — optional cross-cutting logic.
5. `app/api/endpoints/<domain>.py` — the router; include it in `app/api/routes.py`.
6. `alembic revision --autogenerate -m "add <domain>"`.

## Deployment

- **Docker**: `Dockerfile` (API) and `Dockerfile.worker` (background worker).
- **Kubernetes**: `k8s/` (namespace, config, secrets, RBAC, deployment, service, ingress, HPA, PDB). Applied in order by filename.
- **CI** (`.github/workflows/ci.yml`): lint, type-check, migrate, test.
- **CD** (`.github/workflows/cd.yml`): build/push images on tags, deploy to Kubernetes.

## Docker troubleshooting

### `password authentication failed for user "postgres"`

If PostgreSQL reports:

```text
password authentication failed for user "postgres"
```

remember that `POSTGRES_PASSWORD` is only used when the PostgreSQL data directory is initialized.

If the Docker database is disposable, reset the database volume:

```bash
docker compose down -v
docker compose up --build
```

If the database contains data you need, do not remove the volume. Instead, connect to the PostgreSQL instance and change the password for the `postgres` user.

### `port is already in use`

If Docker reports:

```text
listen tcp 0.0.0.0:5432: bind: address already in use
```

another PostgreSQL server is already using host port `5432`.

Expose Docker PostgreSQL on `5433` instead:

```yaml
ports:
  - "5433:5432"
```

Then use:

```text
DBeaver:       localhost:5433
Docker API:    db:5432
Docker Alembic: db:5432
```

### `uvicorn: executable file not found`

If the API fails with:

```text
exec: "uvicorn": executable file not found in $PATH
```

check that the Compose source mount preserves the Docker virtual environment:

```yaml
volumes:
  - ./:/app
  - /app/.venv
```

Then rebuild:

```bash
docker compose down
docker compose up --build
```

### Check container status

```bash
docker compose ps
```

### Inspect the resolved Compose configuration

```bash
docker compose config
```

### Check API environment variables

```bash
docker compose exec api env
```

Avoid printing or sharing environment output when it contains secrets.

## Makefile Docker targets

The recommended Docker-related Make targets are:

```makefile
up:
	docker compose up --build

down:
	docker compose down

docker-build:
	docker compose build

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api

docker-restart:
	docker compose down
	docker compose up -d --build

docker-shell:
	docker compose exec api /bin/bash

docker-clean:
	docker compose down -v
```

## Security notes

Do not commit `.env` files containing real credentials.

Use `.env.example` for non-secret configuration templates and keep `.env` in `.gitignore`.

For production, use your deployment platform's secret management mechanism rather than storing production credentials in the repository.

# schemathesis testing

```sh
schemathesis run http://localhost:8000/openapi.json -H "Authorization: Bearer token_here" --rate-limit 95/m --report ndjson
```