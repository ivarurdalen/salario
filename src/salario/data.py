"""Data acquisition — downloads salary data if not already present."""

import urllib.request
from pathlib import Path

_DATA_URL = (
    "https://www.kode24.no/files/2025/09/01/kode24s%20l%C3%B8nnstall%202025.json"
)
_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "kode24_2025.json"


def ensure_data() -> Path:
    """Return path to the data file, downloading it first if not present."""
    if not _DATA_PATH.exists():
        print(f"Downloading salary data from kode24 → {_DATA_PATH}")
        _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(_DATA_URL, _DATA_PATH)
        print("Download complete.")
    return _DATA_PATH
