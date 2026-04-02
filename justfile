default:
    @just --list

# Start the Panel app locally
start:
    uv run panel serve src/salario/app.py --show --autoreload

# Build the Docker image
build:
    docker build -t salario .

# Run the Docker container
run: build
    docker run --rm -p 5006:5006 salario

# Lint with ruff
lint:
    uv run ruff check src/

# Format with ruff
fmt:
    uv run ruff format src/

# Run tests
test:
    uv run pytest

# Install dependencies
sync:
    uv sync
