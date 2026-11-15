# syntax=docker/dockerfile:1

# Build from the repository root (the tests are in tests/backend/):
#   docker build -f backend/Dockerfile --target test -t synapseitu-backend:test .
#   docker build -f backend/Dockerfile -t synapseitu-backend .

FROM python:3.13.6-slim-bookworm AS base
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
WORKDIR /app/backend

# ---- test: lint, format check and the test suite --------------------------------------
FROM base AS test
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --all-groups --no-install-project
COPY backend/ ./
COPY tests/backend/ /app/tests/backend/
RUN uv run --locked ruff check . ../tests/backend \
 && uv run --locked ruff format --check . ../tests/backend \
 && uv run --locked python -m pytest -q

# ---- runtime: production dependencies only, non-root ------------------------------------
FROM base AS runtime
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY backend/app ./app
RUN useradd --system --uid 1001 synapse
USER synapse
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status == 200 else 1)"
CMD ["/app/backend/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
