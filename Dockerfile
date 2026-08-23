# ── Stage 1: build (Poetry installs deps into a venv) ────────────────────────
FROM python:3.11-slim AS builder

ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml ./
# Install only main deps; no dev tooling in the runtime image.
RUN poetry install --only main --no-root

# ── Stage 2: slim runtime ─────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
