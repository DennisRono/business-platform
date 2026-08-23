.PHONY: help install dev lint format migrate revision up down seed docker-build docker-up docker-down docker-logs docker-restart docker-shell docker-clean

help:
	@echo "Targets:"
	@echo "  install        Install dependencies via Poetry"
	@echo "  dev            Run the API with hot reload"
	@echo "  lint           Run ruff"
	@echo "  format         Run black"
	@echo "  migrate        Apply migrations (alembic upgrade head)"
	@echo "  revision       Autogenerate a migration (msg=...)"
	@echo "  up             Start the local stack (docker compose)"
	@echo "  down           Stop the local stack"
	@echo "  docker-build   Build Docker images"
	@echo "  docker-up      Start Docker containers in detached mode"
	@echo "  docker-down    Stop Docker containers"
	@echo "  docker-logs    Show API container logs"
	@echo "  docker-restart Restart the Docker stack"
	@echo "  docker-shell   Open a shell in the API container"
	@echo "  docker-clean   Stop containers and remove volumes"
	@echo "  seed           Seed permission data"

install:
	poetry install

dev:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	poetry run ruff check .

format:
	poetry run black .

migrate:
	poetry run alembic upgrade head

revision:
	poetry run alembic revision --autogenerate -m "$(msg)"

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

seed:
	poetry run python scripts/seed_permissions.py
	