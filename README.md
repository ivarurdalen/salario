# salario

Salary statistics and tracking for the Norwegian tech industry, based on the [kode24 2025 salary survey](https://www.kode24.no).

## Quick start

```bash
just start
```

Or with Docker:

```bash
just run
```

Open `http://localhost:5006`.

## Commands

```
just start   # Run locally with autoreload
just build   # Build Docker image
just run     # Build and run in Docker
just lint    # Lint with ruff
just fmt     # Format with ruff
just test    # Run tests
just sync    # Install dependencies
```

## Configuration

Edit `config.toml` to set your profile defaults (salary, location, etc.). The file is tracked in the repo with sensible defaults.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `PANEL_PORT` | `5006` | Port the Panel server listens on |
| `PANEL_ADDRESS` | `0.0.0.0` | Bind address |
| `PANEL_ALLOW_WS_ORIGIN` | `*` | Space-separated list of allowed websocket origins |
