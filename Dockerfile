FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.3 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PANEL_ADDRESS=0.0.0.0 \
    PANEL_PORT=5006 \
    PANEL_ALLOW_WS_ORIGIN=*

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md config.toml /app/

RUN --mount=type=cache,target=/root/.cache \
    uv lock && uv sync --frozen --no-dev --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

COPY src /app/src

RUN --mount=type=cache,target=/root/.cache \
    uv sync --frozen --no-dev

COPY docker/start-panel.sh /app/docker/start-panel.sh

RUN chmod +x /app/docker/start-panel.sh

EXPOSE 5006

CMD ["/app/docker/start-panel.sh"]
