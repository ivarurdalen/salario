"""Shared utilities for the salario package."""

from pathlib import Path


def find_root() -> Path:
    """Walk up from the package dir to find the project root (contains pyproject.toml)."""
    d = Path(__file__).resolve().parent
    while d != d.parent:
        if (d / "pyproject.toml").exists():
            return d
        d = d.parent
    return Path.cwd()


ROOT = find_root()
