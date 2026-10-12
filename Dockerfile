FROM python:3.13.6-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --group test

COPY . .

CMD ["/app/.venv/bin/python", "-m", "pytest"]